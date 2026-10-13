using System.Net;
using System.Text;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.Services;

namespace PersonalAIWiki.Core.Tests;

/// <summary>Records requests and answers them from a routing function.</summary>
internal sealed class FakeHandler(Func<HttpRequestMessage, HttpResponseMessage> respond) : HttpMessageHandler
{
    public List<(HttpRequestMessage Request, string? Body)> Requests { get; } = [];

    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var body = request.Content is null ? null : await request.Content.ReadAsStringAsync(ct);
        Requests.Add((request, body));
        return respond(request);
    }

    public static HttpResponseMessage Json(string json, HttpStatusCode status = HttpStatusCode.OK) =>
        new(status) { Content = new StringContent(json, Encoding.UTF8, "application/json") };
}

internal sealed class FakeDialogs : IDialogService
{
    public Queue<bool> ConfirmAnswers { get; } = new();
    public List<string> Confirmations { get; } = [];
    public string? FileToPick { get; set; }

    public bool Confirm(string message, string title = "확인")
    {
        Confirmations.Add(message);
        return ConfirmAnswers.Count > 0 ? ConfirmAnswers.Dequeue() : true;
    }

    public void ShowError(string message, string title = "오류") => Confirmations.Add("ERROR: " + message);
    public void ShowInfo(string message, string title = "알림") { }
    public string? PickFile(string title, string filter) => FileToPick;
    public void OpenExternal(string url) { }
    public void OpenFolder(string path) { }
}

internal sealed class FakeNavigator : INavigator
{
    public List<string> Opened { get; } = [];
    public void NavigateTo(string key) => Opened.Add("nav:" + key);
    public Task OpenWikiPageAsync(string pageId) { Opened.Add("page:" + pageId); return Task.CompletedTask; }
    public Task OpenWikiLinkAsync(string title) { Opened.Add("link:" + title); return Task.CompletedTask; }
    public Task ShowSearchAsync(string query) { Opened.Add("search:" + query); return Task.CompletedTask; }
}

/// <summary>Base fake: every call fails unless a test overrides it.</summary>
internal class StubApi : IPawApi
{
    protected static Exception Nope() => new NotSupportedException("not used by this test");
    public virtual Task<Health> GetHealthAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task<SystemStatus> GetSystemStatusAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task<LlmStatus> GetLlmStatusAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task<AppSettings> GetSettingsAsync(CancellationToken ct = default) => Task.FromResult(new AppSettings { LlmModel = "m", SearchWiki = true });
    public virtual Task<AppSettings> UpdateSettingsAsync(AppSettingsUpdate update, CancellationToken ct = default) => throw Nope();
    public virtual Task<BackupResult> BackupAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task<ReindexResult> ReindexAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task ShutdownAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task<PageList> ListPagesAsync(string status = "active", string? folder = null, string? tag = null, int limit = 500, CancellationToken ct = default) => Task.FromResult(new PageList());
    public virtual Task<Page> GetPageAsync(string pageId, CancellationToken ct = default) => throw Nope();
    public virtual Task<Page> CreatePageAsync(PageCreate page, CancellationToken ct = default) => throw Nope();
    public virtual Task<Page> UpdatePageAsync(string pageId, PageUpdate update, CancellationToken ct = default) => throw Nope();
    public virtual Task<Page> TrashPageAsync(string pageId, CancellationToken ct = default) => throw Nope();
    public virtual Task<Page> RestorePageAsync(string pageId, CancellationToken ct = default) => throw Nope();
    public virtual Task PurgePageAsync(string pageId, CancellationToken ct = default) => throw Nope();
    public virtual Task<IReadOnlyList<RevisionSummary>> ListRevisionsAsync(string pageId, CancellationToken ct = default) => throw Nope();
    public virtual Task<Revision> GetRevisionAsync(string pageId, int number, CancellationToken ct = default) => throw Nope();
    public virtual Task<Page> RestoreRevisionAsync(string pageId, int number, int expectedRevision, CancellationToken ct = default) => throw Nope();
    public virtual Task<Page?> ResolveTitleAsync(string title, CancellationToken ct = default) => throw Nope();
    public virtual Task<IReadOnlyList<FolderInfo>> ListFoldersAsync(CancellationToken ct = default) => throw Nope();
    public virtual Task<Page> ImportFileAsync(string fileName, Stream content, string folder = "", IEnumerable<string>? tags = null, CancellationToken ct = default) => throw Nope();
    public virtual Task<SearchResponse> SearchAsync(string query, string? types = null, int limit = 20, bool group = true, CancellationToken ct = default) => Task.FromResult(new SearchResponse());
    public virtual Task<IReadOnlyList<ChatSession>> ListSessionsAsync(CancellationToken ct = default) => Task.FromResult<IReadOnlyList<ChatSession>>([]);
    public virtual Task<ChatSession> CreateSessionAsync(string? title = null, CancellationToken ct = default) => throw Nope();
    public virtual Task<ChatSessionDetail> GetSessionAsync(string sessionId, CancellationToken ct = default) => throw Nope();
    public virtual Task<ChatSession> RenameSessionAsync(string sessionId, string title, CancellationToken ct = default) => throw Nope();
    public virtual Task DeleteSessionAsync(string sessionId, CancellationToken ct = default) => throw Nope();
    public virtual IAsyncEnumerable<ChatStreamEvent> StreamMessageAsync(string sessionId, SendMessageRequest request, CancellationToken ct = default) => throw Nope();
    public virtual Task<TimelinePage> ListEventsAsync(int limit = 50, string? types = null, string? cursor = null, CancellationToken ct = default) => throw Nope();
}
