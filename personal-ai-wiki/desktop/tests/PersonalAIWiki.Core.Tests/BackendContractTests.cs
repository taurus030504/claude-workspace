using System.Net;
using System.Net.Sockets;
using System.Text;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Backend;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.ViewModels;

namespace PersonalAIWiki.Core.Tests;

/// <summary>
/// Starts the real Python backend (with the deterministic *mock* LLM, not Ollama) through
/// <see cref="BackendLauncher"/> and runs the C# client and view models against it.
/// This checks the C#↔Python API contract end to end. Skipped when the backend's
/// virtual environment is missing (run scripts/setup first) or PAW_SKIP_BACKEND_TESTS=1.
/// </summary>
public sealed class BackendFixture : IAsyncLifetime
{
    private BackendLauncher? _launcher;
    public string? SkipReason { get; private set; }
    public PawApiClient Api { get; private set; } = null!;
    public BackendConnection? Connection { get; private set; }
    public string DataDir { get; } = Directory.CreateTempSubdirectory("paw-contract").FullName;

    public async ValueTask InitializeAsync()
    {
        if (Environment.GetEnvironmentVariable("PAW_SKIP_BACKEND_TESTS") == "1")
        {
            SkipReason = "PAW_SKIP_BACKEND_TESTS=1";
            return;
        }
        var backendDir = PawPaths.FindBackendDirectory(AppContext.BaseDirectory);
        if (backendDir is null || !File.Exists(PawPaths.DefaultPython(backendDir)))
        {
            SkipReason = "backend virtual environment not found; run scripts/setup first";
            return;
        }
        var options = new BackendOptions
        {
            BaseUrl = $"http://127.0.0.1:{FreePort()}/",
            DataDir = DataDir,
            BackendDirectory = backendDir,
            Environment = { ["PAW_LLM_PROVIDER"] = "mock", ["PAW_OLLAMA_MODEL"] = "mock-model" },
        };
        _launcher = new BackendLauncher(options);
        Connection = await _launcher.ConnectAsync();
        if (Connection.Api is null) throw new InvalidOperationException("backend failed to start: " + Connection.Message);
        Api = Connection.Api;
    }

    public async ValueTask DisposeAsync()
    {
        if (_launcher is not null) await _launcher.DisposeAsync();
        try { Directory.Delete(DataDir, recursive: true); } catch (IOException) { }
    }

    private static int FreePort()
    {
        var l = new TcpListener(IPAddress.Loopback, 0);
        l.Start();
        var port = ((IPEndPoint)l.LocalEndpoint).Port;
        l.Stop();
        return port;
    }
}

public class BackendContractTests(BackendFixture fx) : IClassFixture<BackendFixture>
{
    private CancellationToken Ct => TestContext.Current.CancellationToken;

    private void SkipIfUnavailable() => Assert.SkipWhen(fx.SkipReason is not null, fx.SkipReason ?? "");

    [Fact]
    public async Task Launcher_started_backend_and_reads_token()
    {
        SkipIfUnavailable();
        Assert.Equal(BackendState.Started, fx.Connection!.State);
        Assert.True(File.Exists(PawPaths.TokenPath(fx.DataDir)));
        var health = await fx.Api.GetHealthAsync(Ct);
        Assert.Equal("ok", health.Status);
        Assert.True(health.SchemaVersion >= 1);
        var llm = await fx.Api.GetLlmStatusAsync(Ct);
        Assert.Equal("mock", llm.Provider);
        Assert.True(llm.ModelAvailable);
    }

    [Fact]
    public async Task Wiki_crud_revisions_conflict_and_search()
    {
        SkipIfUnavailable();
        var api = fx.Api;
        var page = await api.CreatePageAsync(new PageCreate { Title = "계약 테스트 문서", Content = "# 개요\n창 고정 메커니즘 설명", Folder = "테스트", Tags = ["계약"] }, Ct);
        Assert.Equal(1, page.CurrentRevision);

        var updated = await api.UpdatePageAsync(page.PageId, new PageUpdate { ExpectedRevision = 1, Content = "# 개요\n창 고정과 반동 점프" }, Ct);
        Assert.Equal(2, updated.CurrentRevision);

        var conflict = await Assert.ThrowsAsync<ApiException>(() =>
            api.UpdatePageAsync(page.PageId, new PageUpdate { ExpectedRevision = 1, Content = "stale" }, Ct));
        Assert.True(conflict.IsConflict);
        Assert.Equal(2, conflict.DetailInt("current_revision"));

        var revisions = await api.ListRevisionsAsync(page.PageId, Ct);
        Assert.Equal([2, 1], revisions.Select(r => r.RevisionNumber));

        var hits = await api.SearchAsync("반동 점프는?", ct: Ct);
        var hit = hits.Items.First(h => h.EntityId == page.PageId);
        Assert.Equal("개요", hit.Heading);
        Assert.NotEmpty(hit.Highlights);
        Assert.All(hit.Highlights, h => Assert.Equal(2, h.Length));

        Assert.Equal(page.PageId, (await api.ResolveTitleAsync("계약 테스트 문서", Ct))!.PageId);
        Assert.Null(await api.ResolveTitleAsync("존재하지 않는 문서", Ct));

        var trashed = await api.TrashPageAsync(page.PageId, Ct);
        Assert.True(trashed.IsDeleted);
        Assert.DoesNotContain((await api.SearchAsync("반동 점프", ct: Ct)).Items, h => h.EntityId == page.PageId);
        await api.PurgePageAsync(page.PageId, Ct);
        var gone = await Assert.ThrowsAsync<ApiException>(() => api.GetPageAsync(page.PageId, Ct));
        Assert.True(gone.IsNotFound);
    }

    [Fact]
    public async Task Import_text_file_with_korean_encoding()
    {
        SkipIfUnavailable();
        Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
        var bytes = Encoding.GetEncoding(949).GetBytes("메모장으로 쓴 한국어 파일");
        using var stream = new MemoryStream(bytes);
        var page = await fx.Api.ImportFileAsync("메모.txt", stream, "가져옴", ["import"], Ct);
        Assert.Equal("메모", page.Title);
        Assert.Equal("메모장으로 쓴 한국어 파일", page.Content);
        Assert.Equal("import_file", page.SourceType);

        var pdf = await Assert.ThrowsAsync<ApiException>(() => fx.Api.ImportFileAsync("a.pdf", new MemoryStream([1, 2, 3]), ct: Ct));
        Assert.Equal(HttpStatusCode.UnsupportedMediaType, pdf.Status);
    }

    [Fact]
    public async Task Chat_view_model_streams_from_backend_with_citations()
    {
        SkipIfUnavailable();
        await fx.Api.CreatePageAsync(new PageCreate { Title = "스테이지 설계", Content = "1단계는 성벽 오르기 튜토리얼이다." }, Ct);
        var nav = new FakeNavigator();
        var vm = new ChatViewModel(fx.Api, new FakeDialogs(), nav);
        await vm.InitializeAsync();
        vm.Input = "1단계 스테이지는 어떤 내용이야?";
        await vm.SendAsync();

        var answer = vm.Messages.Last();
        Assert.Null(answer.ErrorText);
        Assert.StartsWith("[모의 응답]", answer.Content);
        Assert.Equal("complete", answer.Status);
        var source = Assert.Single(vm.LastSources, s => s.Title == "스테이지 설계");
        Assert.True(source.Cited);
        Assert.Contains(vm.Sessions, s => s.SessionId == vm.CurrentSessionId && s.Title.StartsWith("1단계"));

        // reloading the session from the backend shows the same conversation
        await vm.LoadSessionAsync(vm.CurrentSessionId!);
        Assert.Equal(["user", "assistant"], vm.Messages.Select(m => m.Role));
        Assert.Equal("스테이지 설계", vm.Messages[1].Sources.First().Title);
    }

    [Fact]
    public async Task Wiki_view_model_round_trip()
    {
        SkipIfUnavailable();
        var vm = new WikiViewModel(fx.Api, new FakeDialogs(), new FakeNavigator());
        vm.NewPage();
        vm.EditTitle = "뷰모델 문서";
        vm.EditFolder = "테스트/뷰모델";
        vm.EditTags = "a, b";
        vm.EditContent = "본문 [[다른 문서]]";
        await vm.SaveAsync();

        Assert.Null(vm.ErrorMessage);
        Assert.False(vm.IsDirty);
        Assert.Equal(["다른 문서"], vm.CurrentPage!.Links);
        Assert.Contains(vm.AllPages, p => p.Title == "뷰모델 문서");

        vm.EditContent = "수정된 본문";
        await vm.SaveAsync();
        Assert.Equal(2, vm.CurrentPage!.CurrentRevision);

        await vm.ToggleHistoryAsync();
        Assert.Equal(2, vm.Revisions.Count);
        await vm.RestoreRevisionAsync(vm.Revisions.Last());
        Assert.Equal("본문 [[다른 문서]]", vm.EditContent);
        Assert.Equal(3, vm.CurrentPage!.CurrentRevision);

        var settings = await fx.Api.UpdateSettingsAsync(new AppSettingsUpdate { SearchWiki = false }, Ct);
        Assert.False(settings.SearchWiki);
        await fx.Api.UpdateSettingsAsync(new AppSettingsUpdate { SearchWiki = true }, Ct);

        var events = await fx.Api.ListEventsAsync(ct: Ct);
        Assert.Contains(events.Items, e => e.EventType == "wiki_page_created" && e.SourceId == vm.CurrentPage.PageId);
        Assert.True((await fx.Api.BackupAsync(Ct)).SizeBytes > 0);
    }
}
