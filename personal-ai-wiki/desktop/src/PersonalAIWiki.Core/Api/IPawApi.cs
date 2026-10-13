using PersonalAIWiki.Core.Models;

namespace PersonalAIWiki.Core.Api;

/// <summary>Typed access to the local backend REST API (see docs/API.md).
/// The UI never touches the database; everything goes through this interface.</summary>
public interface IPawApi
{
    // System
    Task<Health> GetHealthAsync(CancellationToken ct = default);
    Task<SystemStatus> GetSystemStatusAsync(CancellationToken ct = default);
    Task<LlmStatus> GetLlmStatusAsync(CancellationToken ct = default);
    Task<AppSettings> GetSettingsAsync(CancellationToken ct = default);
    Task<AppSettings> UpdateSettingsAsync(AppSettingsUpdate update, CancellationToken ct = default);
    Task<BackupResult> BackupAsync(CancellationToken ct = default);
    Task<ReindexResult> ReindexAsync(CancellationToken ct = default);
    Task ShutdownAsync(CancellationToken ct = default);

    // Wiki
    Task<PageList> ListPagesAsync(string status = "active", string? folder = null, string? tag = null, int limit = 500, CancellationToken ct = default);
    Task<Page> GetPageAsync(string pageId, CancellationToken ct = default);
    Task<Page> CreatePageAsync(PageCreate page, CancellationToken ct = default);
    Task<Page> UpdatePageAsync(string pageId, PageUpdate update, CancellationToken ct = default);
    Task<Page> TrashPageAsync(string pageId, CancellationToken ct = default);
    Task<Page> RestorePageAsync(string pageId, CancellationToken ct = default);
    Task PurgePageAsync(string pageId, CancellationToken ct = default);
    Task<IReadOnlyList<RevisionSummary>> ListRevisionsAsync(string pageId, CancellationToken ct = default);
    Task<Revision> GetRevisionAsync(string pageId, int number, CancellationToken ct = default);
    Task<Page> RestoreRevisionAsync(string pageId, int number, int expectedRevision, CancellationToken ct = default);
    Task<Page?> ResolveTitleAsync(string title, CancellationToken ct = default);
    Task<IReadOnlyList<FolderInfo>> ListFoldersAsync(CancellationToken ct = default);
    Task<Page> ImportFileAsync(string fileName, Stream content, string folder = "", IEnumerable<string>? tags = null, CancellationToken ct = default);

    // Search
    Task<SearchResponse> SearchAsync(string query, string? types = null, int limit = 20, bool group = true, CancellationToken ct = default);

    // Chat
    Task<IReadOnlyList<ChatSession>> ListSessionsAsync(CancellationToken ct = default);
    Task<ChatSession> CreateSessionAsync(string? title = null, CancellationToken ct = default);
    Task<ChatSessionDetail> GetSessionAsync(string sessionId, CancellationToken ct = default);
    Task<ChatSession> RenameSessionAsync(string sessionId, string title, CancellationToken ct = default);
    Task DeleteSessionAsync(string sessionId, CancellationToken ct = default);
    IAsyncEnumerable<ChatStreamEvent> StreamMessageAsync(string sessionId, SendMessageRequest request, CancellationToken ct = default);

    // Timeline
    Task<TimelinePage> ListEventsAsync(int limit = 50, string? types = null, string? cursor = null, CancellationToken ct = default);
}
