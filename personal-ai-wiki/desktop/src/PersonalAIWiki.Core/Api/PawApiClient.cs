using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using PersonalAIWiki.Core.Models;

namespace PersonalAIWiki.Core.Api;

public sealed class PawApiClient : IPawApi, IDisposable
{
    public const string TokenHeader = "X-PAW-Token";
    private static readonly TimeSpan RequestTimeout = TimeSpan.FromSeconds(60);

    private readonly HttpClient _http;
    private readonly bool _ownsClient;

    public PawApiClient(Uri baseUrl, string token, HttpMessageHandler? handler = null)
    {
        _http = handler is null ? new HttpClient() : new HttpClient(handler);
        _ownsClient = true;
        _http.BaseAddress = baseUrl;
        // Streaming answers on CPU can take minutes; per-request timeouts are applied below instead.
        _http.Timeout = Timeout.InfiniteTimeSpan;
        _http.DefaultRequestHeaders.Add(TokenHeader, token);
    }

    public void Dispose()
    {
        if (_ownsClient) _http.Dispose();
    }

    // ------------------------------------------------------------------ System
    public Task<Health> GetHealthAsync(CancellationToken ct = default) => Get<Health>("api/v1/health", ct);
    public Task<SystemStatus> GetSystemStatusAsync(CancellationToken ct = default) => Get<SystemStatus>("api/v1/system/status", ct);
    public Task<LlmStatus> GetLlmStatusAsync(CancellationToken ct = default) => Get<LlmStatus>("api/v1/system/llm", ct);
    public Task<AppSettings> GetSettingsAsync(CancellationToken ct = default) => Get<AppSettings>("api/v1/settings", ct);
    public Task<AppSettings> UpdateSettingsAsync(AppSettingsUpdate update, CancellationToken ct = default) => Send<AppSettings>(HttpMethod.Patch, "api/v1/settings", update, ct);
    public Task<BackupResult> BackupAsync(CancellationToken ct = default) => Send<BackupResult>(HttpMethod.Post, "api/v1/system/backup", null, ct);
    public Task<ReindexResult> ReindexAsync(CancellationToken ct = default) => Send<ReindexResult>(HttpMethod.Post, "api/v1/system/reindex", null, ct);
    public Task ShutdownAsync(CancellationToken ct = default) => SendNoContent(HttpMethod.Post, "api/v1/system/shutdown", ct);

    // ------------------------------------------------------------------ Wiki
    public Task<PageList> ListPagesAsync(string status = "active", string? folder = null, string? tag = null, int limit = 500, CancellationToken ct = default)
        => Get<PageList>("api/v1/wiki/pages" + Query(("status", status), ("folder", folder), ("tag", tag), ("limit", limit.ToString())), ct);

    public Task<Page> GetPageAsync(string pageId, CancellationToken ct = default) => Get<Page>($"api/v1/wiki/pages/{Esc(pageId)}", ct);
    public Task<Page> CreatePageAsync(PageCreate page, CancellationToken ct = default) => Send<Page>(HttpMethod.Post, "api/v1/wiki/pages", page, ct);
    public Task<Page> UpdatePageAsync(string pageId, PageUpdate update, CancellationToken ct = default) => Send<Page>(HttpMethod.Patch, $"api/v1/wiki/pages/{Esc(pageId)}", update, ct);
    public Task<Page> TrashPageAsync(string pageId, CancellationToken ct = default) => Send<Page>(HttpMethod.Delete, $"api/v1/wiki/pages/{Esc(pageId)}", null, ct);
    public Task<Page> RestorePageAsync(string pageId, CancellationToken ct = default) => Send<Page>(HttpMethod.Post, $"api/v1/wiki/pages/{Esc(pageId)}/restore", null, ct);
    public Task PurgePageAsync(string pageId, CancellationToken ct = default) => SendNoContent(HttpMethod.Delete, $"api/v1/wiki/pages/{Esc(pageId)}?permanent=true", ct);

    public Task<IReadOnlyList<RevisionSummary>> ListRevisionsAsync(string pageId, CancellationToken ct = default)
        => Get<IReadOnlyList<RevisionSummary>>($"api/v1/wiki/pages/{Esc(pageId)}/revisions", ct);

    public Task<Revision> GetRevisionAsync(string pageId, int number, CancellationToken ct = default)
        => Get<Revision>($"api/v1/wiki/pages/{Esc(pageId)}/revisions/{number}", ct);

    public Task<Page> RestoreRevisionAsync(string pageId, int number, int expectedRevision, CancellationToken ct = default)
        => Send<Page>(HttpMethod.Post, $"api/v1/wiki/pages/{Esc(pageId)}/revisions/{number}/restore", new { ExpectedRevision = expectedRevision }, ct);

    public async Task<Page?> ResolveTitleAsync(string title, CancellationToken ct = default)
    {
        try
        {
            return await Get<Page>("api/v1/wiki/resolve" + Query(("title", title)), ct).ConfigureAwait(false);
        }
        catch (ApiException e) when (e.IsNotFound)
        {
            return null;
        }
    }

    public Task<IReadOnlyList<FolderInfo>> ListFoldersAsync(CancellationToken ct = default) => Get<IReadOnlyList<FolderInfo>>("api/v1/wiki/folders", ct);

    public async Task<Page> ImportFileAsync(string fileName, Stream content, string folder = "", IEnumerable<string>? tags = null, CancellationToken ct = default)
    {
        using var form = new MultipartFormDataContent();
        var file = new StreamContent(content);
        file.Headers.ContentType = new("application/octet-stream");
        form.Add(file, "file", fileName);
        form.Add(new StringContent(folder, Encoding.UTF8), "folder");
        form.Add(new StringContent(string.Join(",", tags ?? []), Encoding.UTF8), "tags");
        using var req = new HttpRequestMessage(HttpMethod.Post, "api/v1/wiki/import") { Content = form };
        return await Execute<Page>(req, ct).ConfigureAwait(false);
    }

    // ------------------------------------------------------------------ Search
    public Task<SearchResponse> SearchAsync(string query, string? types = null, int limit = 20, bool group = true, CancellationToken ct = default)
        => Get<SearchResponse>("api/v1/search" + Query(("q", query), ("types", types), ("limit", limit.ToString()), ("group", group ? "true" : "false")), ct);

    // ------------------------------------------------------------------ Chat
    public Task<IReadOnlyList<ChatSession>> ListSessionsAsync(CancellationToken ct = default) => Get<IReadOnlyList<ChatSession>>("api/v1/chat/sessions", ct);
    public Task<ChatSession> CreateSessionAsync(string? title = null, CancellationToken ct = default) => Send<ChatSession>(HttpMethod.Post, "api/v1/chat/sessions", new { Title = title }, ct);
    public Task<ChatSessionDetail> GetSessionAsync(string sessionId, CancellationToken ct = default) => Get<ChatSessionDetail>($"api/v1/chat/sessions/{Esc(sessionId)}", ct);
    public Task<ChatSession> RenameSessionAsync(string sessionId, string title, CancellationToken ct = default) => Send<ChatSession>(HttpMethod.Patch, $"api/v1/chat/sessions/{Esc(sessionId)}", new { Title = title }, ct);
    public Task DeleteSessionAsync(string sessionId, CancellationToken ct = default) => SendNoContent(HttpMethod.Delete, $"api/v1/chat/sessions/{Esc(sessionId)}", ct);

    public async IAsyncEnumerable<ChatStreamEvent> StreamMessageAsync(
        string sessionId, SendMessageRequest request, [EnumeratorCancellation] CancellationToken ct = default)
    {
        var body = new SendMessageRequest { Content = request.Content, Stream = true, Model = request.Model, UseWiki = request.UseWiki };
        using var req = new HttpRequestMessage(HttpMethod.Post, $"api/v1/chat/sessions/{Esc(sessionId)}/messages")
        {
            Content = JsonContent.Create(body, options: PawJson.Options),
        };
        HttpResponseMessage resp;
        try
        {
            resp = await _http.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct).ConfigureAwait(false);
        }
        catch (HttpRequestException e)
        {
            throw Unreachable(e);
        }
        using (resp)
        {
            if (!resp.IsSuccessStatusCode)
            {
                throw ApiException.FromBody(resp.StatusCode, await resp.Content.ReadAsStringAsync(ct).ConfigureAwait(false));
            }
            await using var stream = await resp.Content.ReadAsStreamAsync(ct).ConfigureAwait(false);
            using var reader = new StreamReader(stream, Encoding.UTF8);
            while (await reader.ReadLineAsync(ct).ConfigureAwait(false) is { } line)
            {
                if (string.IsNullOrWhiteSpace(line)) continue;
                var ev = JsonSerializer.Deserialize<ChatStreamEvent>(line, PawJson.Options);
                if (ev is not null) yield return ev;
            }
        }
    }

    // ------------------------------------------------------------------ Timeline
    public Task<TimelinePage> ListEventsAsync(int limit = 50, string? types = null, string? cursor = null, CancellationToken ct = default)
        => Get<TimelinePage>("api/v1/timeline/events" + Query(("limit", limit.ToString()), ("types", types), ("cursor", cursor)), ct);

    // ------------------------------------------------------------------ plumbing
    private Task<T> Get<T>(string path, CancellationToken ct) => Send<T>(HttpMethod.Get, path, null, ct);

    private async Task<T> Send<T>(HttpMethod method, string path, object? body, CancellationToken ct)
    {
        using var req = new HttpRequestMessage(method, path);
        if (body is not null) req.Content = JsonContent.Create(body, body.GetType(), options: PawJson.Options);
        return await Execute<T>(req, ct).ConfigureAwait(false);
    }

    private async Task SendNoContent(HttpMethod method, string path, CancellationToken ct)
    {
        using var req = new HttpRequestMessage(method, path);
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(RequestTimeout);
        using var resp = await Transport(req, cts.Token).ConfigureAwait(false);
        if (!resp.IsSuccessStatusCode)
            throw ApiException.FromBody(resp.StatusCode, await resp.Content.ReadAsStringAsync(cts.Token).ConfigureAwait(false));
    }

    private async Task<T> Execute<T>(HttpRequestMessage req, CancellationToken ct)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(RequestTimeout);
        using var resp = await Transport(req, cts.Token).ConfigureAwait(false);
        var text = await resp.Content.ReadAsStringAsync(cts.Token).ConfigureAwait(false);
        if (!resp.IsSuccessStatusCode) throw ApiException.FromBody(resp.StatusCode, text);
        return JsonSerializer.Deserialize<T>(text, PawJson.Options)
               ?? throw new ApiException(resp.StatusCode, "empty_response", "backend returned an empty response");
    }

    private async Task<HttpResponseMessage> Transport(HttpRequestMessage req, CancellationToken ct)
    {
        try
        {
            return await _http.SendAsync(req, ct).ConfigureAwait(false);
        }
        catch (HttpRequestException e)
        {
            throw Unreachable(e);
        }
    }

    private static ApiException Unreachable(Exception e) =>
        new(null, "backend_unreachable", "백엔드 서버에 연결할 수 없습니다. 앱을 다시 시작하거나 백엔드 로그를 확인하세요.", inner: e);

    private static string Esc(string s) => Uri.EscapeDataString(s);

    internal static string Query(params (string Key, string? Value)[] pairs)
    {
        var parts = pairs.Where(p => p.Value is not null).Select(p => $"{p.Key}={Uri.EscapeDataString(p.Value!)}").ToList();
        return parts.Count == 0 ? "" : "?" + string.Join("&", parts);
    }
}

