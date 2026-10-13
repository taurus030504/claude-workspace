using System.Net;
using System.Runtime.CompilerServices;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Backend;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.ViewModels;

namespace PersonalAIWiki.Core.Tests;

public class WikiTreeTests
{
    private static PageSummary P(string title, string folder = "", params string[] tags) =>
        new() { PageId = title, Title = title, Folder = folder, Tags = tags };

    [Fact]
    public void Builds_nested_folders_before_pages_sorted()
    {
        var tree = WikiTree.Build([P("Zeta"), P("창 물리", "게임/시스템"), P("GDD", "게임"), P("alpha"), P("카메라", "게임/시스템")]);

        Assert.Equal(["게임", "alpha", "Zeta"], tree.Select(n => n.Name));
        var game = Assert.IsType<FolderNode>(tree[0]);
        Assert.Equal(["시스템", "GDD"], game.Children.Select(n => n.Name));
        var sys = Assert.IsType<FolderNode>(game.Children[0]);
        Assert.Equal("게임/시스템", sys.Path);
        Assert.Equal(["창 물리", "카메라"], sys.Children.Select(n => n.Name));
        Assert.Equal(3, game.PageCount);
    }

    [Fact]
    public void Filter_matches_title_folder_or_tag()
    {
        var pages = new[] { P("창 물리", "게임"), P("레시피", "요리", "찌개"), P("기타") };
        Assert.Single(WikiTree.Build(pages, "찌개"));
        Assert.Equal("게임", WikiTree.Build(pages, "게임").Single().Name);
        Assert.Empty(WikiTree.Build(pages, "없음"));
    }
}

public class WikiViewModelUnitTests
{
    private sealed class ConflictApi : StubApi
    {
        public int Gets;
        public override Task<Page> GetPageAsync(string pageId, CancellationToken ct = default)
        {
            Gets++;
            return Task.FromResult(new Page { PageId = "p", Title = "서버 제목", Content = "server", CurrentRevision = Gets == 1 ? 1 : 2 });
        }

        public override Task<Page> UpdatePageAsync(string pageId, PageUpdate update, CancellationToken ct = default) =>
            throw new ApiException(HttpStatusCode.Conflict, "conflict", "reload",
                System.Text.Json.JsonDocument.Parse("""{"current_revision":2}""").RootElement.Clone());
    }

    [Fact]
    public async Task Dirty_tracking_and_tag_parsing()
    {
        var vm = new WikiViewModel(new StubApi(), new FakeDialogs(), new FakeNavigator());
        Assert.False(vm.IsDirty);
        vm.NewPage();
        Assert.True(vm.IsNew);
        Assert.False(vm.SaveCommand.CanExecute(null)); // empty title
        vm.EditTitle = "새 문서";
        Assert.True(vm.IsDirty);
        Assert.True(vm.SaveCommand.CanExecute(null));
        Assert.Equal(["게임", "물리"], WikiViewModel.ParseTags(" #물리, 게임;; 물리 "));
        Assert.Equal("게임/설계", WikiViewModel.NormalizeFolder(@" 게임\ /설계/ "));
        await Task.CompletedTask;
    }

    [Fact]
    public async Task Save_conflict_asks_and_reloads_server_version()
    {
        var api = new ConflictApi();
        var dialogs = new FakeDialogs();
        var vm = new WikiViewModel(api, dialogs, new FakeNavigator());
        await vm.OpenPageAsync("p");
        vm.EditContent = "my local edit";
        dialogs.ConfirmAnswers.Enqueue(true); // reload

        await vm.SaveAsync();

        Assert.Contains("현재 리비전 2", dialogs.Confirmations.Single());
        Assert.Equal("server", vm.EditContent);
        Assert.Equal(2, vm.CurrentPage!.CurrentRevision);
        Assert.False(vm.IsDirty);
    }

    [Fact]
    public async Task Save_conflict_can_keep_local_edits()
    {
        var dialogs = new FakeDialogs();
        var vm = new WikiViewModel(new ConflictApi(), dialogs, new FakeNavigator());
        await vm.OpenPageAsync("p");
        vm.EditContent = "keep me";
        dialogs.ConfirmAnswers.Enqueue(false);
        await vm.SaveAsync();
        Assert.Equal("keep me", vm.EditContent);
        Assert.True(vm.IsDirty);
    }

    [Fact]
    public async Task Switching_pages_with_unsaved_changes_requires_confirmation()
    {
        var dialogs = new FakeDialogs();
        var vm = new WikiViewModel(new ConflictApi(), dialogs, new FakeNavigator());
        vm.NewPage();
        vm.EditContent = "draft";
        dialogs.ConfirmAnswers.Enqueue(false); // keep editing
        await vm.OpenPageAsync("p");
        Assert.True(vm.IsNew);
        Assert.Equal("draft", vm.EditContent);
    }
}

public class ChatViewModelUnitTests
{
    private sealed class UnavailableApi : StubApi
    {
        public readonly List<string> Deleted = [];
        public override Task<ChatSession> CreateSessionAsync(string? title = null, CancellationToken ct = default) =>
            Task.FromResult(new ChatSession { SessionId = "s1", Title = "새 대화" });
        public override Task DeleteSessionAsync(string sessionId, CancellationToken ct = default)
        {
            Deleted.Add(sessionId);
            return Task.CompletedTask;
        }
        public override IAsyncEnumerable<ChatStreamEvent> StreamMessageAsync(string sessionId, SendMessageRequest request, CancellationToken ct = default) =>
            throw new ApiException(HttpStatusCode.ServiceUnavailable, "llm_unavailable", "'ollama pull gemma3:4b'을 실행하세요.");
    }

    private sealed class StreamingApi : StubApi
    {
        public override Task<ChatSession> CreateSessionAsync(string? title = null, CancellationToken ct = default) =>
            Task.FromResult(new ChatSession { SessionId = "s1" });

        public override async IAsyncEnumerable<ChatStreamEvent> StreamMessageAsync(
            string sessionId, SendMessageRequest request, [EnumeratorCancellation] CancellationToken ct = default)
        {
            var src = new SourceRef { Number = 1, SourceType = "wiki_page", SourceId = "p1", Title = "창 물리" };
            yield return new ChatStreamEvent { Type = "start", Sources = [src], Model = "m" };
            foreach (var piece in new[] { "창은 ", "벽에 고정", "됩니다 [1]" })
            {
                await Task.Yield();
                yield return new ChatStreamEvent { Type = "delta", Text = piece };
            }
            yield return new ChatStreamEvent
            {
                Type = "done",
                AssistantMessage = new ChatMessage { Role = "assistant", Content = "창은 벽에 고정됩니다 [1]", Sources = [new SourceRef { Number = 1, SourceId = "p1", SourceType = "wiki_page", Title = "창 물리", Cited = true }] },
            };
        }
    }

    [Fact]
    public async Task Streams_answer_and_exposes_sources()
    {
        var nav = new FakeNavigator();
        var vm = new ChatViewModel(new StreamingApi(), new FakeDialogs(), nav, compact: true);
        vm.Input = "창은?";
        await vm.SendAsync();

        Assert.Equal(2, vm.Messages.Count);
        var answer = vm.Messages[1];
        Assert.Equal("창은 벽에 고정됩니다 [1]", answer.Content);
        Assert.Equal("complete", answer.Status);
        Assert.False(answer.IsStreaming);
        Assert.True(vm.LastSources.Single().Cited);
        await vm.OpenSourceCommand.ExecuteAsync(vm.LastSources[0]);
        Assert.Equal(["page:p1"], nav.Opened);
        Assert.Equal("", vm.Input);
    }

    [Fact]
    public async Task Llm_unavailable_restores_question_and_cleans_up_empty_session()
    {
        var api = new UnavailableApi();
        var vm = new ChatViewModel(api, new FakeDialogs(), new FakeNavigator(), compact: true);
        vm.Input = "질문";
        await vm.SendAsync();

        Assert.Empty(vm.Messages);
        Assert.Equal("질문", vm.Input);
        Assert.Contains("ollama pull", vm.LlmProblem);
        Assert.Equal(["s1"], api.Deleted);
        Assert.Null(vm.CurrentSessionId);
        Assert.False(vm.IsSending);
    }
}

public class BackendOptionsTests
{
    [Fact]
    public void Loads_options_and_treats_blank_as_auto()
    {
        var path = Path.Combine(Path.GetTempPath(), $"paw-{Guid.NewGuid():N}.json");
        File.WriteAllText(path, """
            {
              // comment allowed
              "Backend": { "BaseUrl": "http://127.0.0.1:9000", "DataDir": "", "AutoStart": false, "Environment": { "PAW_OLLAMA_MODEL": "exaone3.5:2.4b" } }
            }
            """);
        var o = BackendOptions.Load(path);
        Assert.Equal(new Uri("http://127.0.0.1:9000/"), o.BaseUri);
        Assert.Null(o.DataDir);
        Assert.False(o.AutoStart);
        Assert.Equal("exaone3.5:2.4b", o.Environment["PAW_OLLAMA_MODEL"]);
        Assert.True(BackendOptions.Load(path + ".missing").AutoStart);
    }

    [Fact]
    public void Finds_backend_directory_walking_up()
    {
        var root = Directory.CreateTempSubdirectory("paw");
        Directory.CreateDirectory(Path.Combine(root.FullName, "backend", "app"));
        File.WriteAllText(Path.Combine(root.FullName, "backend", "app", "__init__.py"), "");
        var deep = Directory.CreateDirectory(Path.Combine(root.FullName, "desktop", "bin", "Debug", "net10.0"));
        Assert.Equal(Path.Combine(root.FullName, "backend"), PawPaths.FindBackendDirectory(deep.FullName));
    }
}

public class ConcurrencyTests
{
    private sealed class SlowApi : StubApi
    {
        public override async Task<SystemStatus> GetSystemStatusAsync(CancellationToken ct = default)
        {
            await Task.Delay(20, ct);
            return new SystemStatus();
        }
        public override Task<LlmStatus> GetLlmStatusAsync(CancellationToken ct = default) => Task.FromResult(new LlmStatus());
        public override async Task<PageList> ListPagesAsync(string status = "active", string? folder = null, string? tag = null, int limit = 500, CancellationToken ct = default)
        {
            await Task.Delay(10, ct);
            return new PageList { Items = [new PageSummary { PageId = "a", Title = "A" }, new PageSummary { PageId = "b", Title = "B" }] };
        }
        public override Task<TimelinePage> ListEventsAsync(int limit = 50, string? types = null, string? cursor = null, CancellationToken ct = default) =>
            Task.FromResult(new TimelinePage { Items = [new TimelineEvent { EventId = "e" }] });
    }

    [Fact]
    public async Task Overlapping_refreshes_do_not_duplicate_items()
    {
        var dash = new DashboardViewModel(new SlowApi(), new FakeNavigator());
        await Task.WhenAll(dash.RefreshAsync(), dash.RefreshAsync(), dash.RefreshAsync());
        Assert.Equal(2, dash.RecentPages.Count);
        Assert.Single(dash.RecentEvents);

        var wiki = new WikiViewModel(new SlowApi(), new FakeDialogs(), new FakeNavigator()) { ShowTrash = true };
        await Task.WhenAll(wiki.LoadAsync(), wiki.LoadAsync());
        Assert.Equal(2, wiki.TrashPages.Count);
        Assert.Equal(2, wiki.Tree.Count);
    }
}
