using System.Net;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Models;

namespace PersonalAIWiki.Core.Tests;

/// <summary>PawApiClient against canned HTTP responses (no backend needed).</summary>
public class ApiClientTests
{
    private static PawApiClient Client(FakeHandler h) => new(new Uri("http://127.0.0.1:8765/"), "tok123", h);

    [Fact]
    public async Task Sends_token_and_maps_snake_case_json()
    {
        var h = new FakeHandler(_ => FakeHandler.Json("""
            {"page_id":"p1","title":"게임 설계","folder":"게임","content":"# x","tags":["a"],"summary":null,
             "source_type":"user","source_ref":null,"current_revision":3,"status":"active","links":["창"],
             "created_at":"2026-10-01T00:00:00.000Z","updated_at":"2026-10-02T12:30:00.000Z","deleted_at":null}
            """));
        var page = await Client(h).GetPageAsync("p1", TestContext.Current.CancellationToken);

        Assert.Equal("게임 설계", page.Title);
        Assert.Equal(3, page.CurrentRevision);
        Assert.Equal(["창"], page.Links);
        Assert.Equal(new DateTimeOffset(2026, 10, 2, 12, 30, 0, TimeSpan.Zero), page.UpdatedAt);
        var req = h.Requests.Single().Request;
        Assert.Equal("tok123", req.Headers.GetValues(PawApiClient.TokenHeader).Single());
        Assert.Equal("/api/v1/wiki/pages/p1", req.RequestUri!.AbsolutePath);
    }

    [Fact]
    public async Task Partial_update_omits_null_fields()
    {
        var h = new FakeHandler(_ => FakeHandler.Json("""{"page_id":"p1","title":"t","current_revision":2}"""));
        await Client(h).UpdatePageAsync("p1", new PageUpdate { ExpectedRevision = 1, Content = "new" }, TestContext.Current.CancellationToken);
        Assert.Equal("""{"expected_revision":1,"content":"new"}""", h.Requests.Single().Body);
    }

    [Fact]
    public async Task Error_envelope_becomes_ApiException_with_details()
    {
        var h = new FakeHandler(_ => FakeHandler.Json(
            """{"error":{"code":"conflict","message":"reload","details":{"current_revision":7}}}""", HttpStatusCode.Conflict));
        var e = await Assert.ThrowsAsync<ApiException>(() =>
            Client(h).UpdatePageAsync("p1", new PageUpdate { ExpectedRevision = 1 }, TestContext.Current.CancellationToken));
        Assert.True(e.IsConflict);
        Assert.Equal("conflict", e.Code);
        Assert.Equal(7, e.DetailInt("current_revision"));
    }

    [Fact]
    public async Task Resolve_title_returns_null_on_404_and_encodes_query()
    {
        var h = new FakeHandler(_ => FakeHandler.Json("""{"error":{"code":"not_found","message":"x"}}""", HttpStatusCode.NotFound));
        Assert.Null(await Client(h).ResolveTitleAsync("창 물리 & 반동", TestContext.Current.CancellationToken));
        Assert.Contains("title=%EC%B0%BD%20%EB%AC%BC%EB%A6%AC%20%26%20%EB%B0%98%EB%8F%99", h.Requests.Single().Request.RequestUri!.Query);
    }

    [Fact]
    public async Task Streams_ndjson_events_in_order()
    {
        const string body = """
            {"type":"start","user_message":{"message_id":"u","role":"user","content":"q"},"sources":[{"number":1,"source_type":"wiki_page","source_id":"p1","title":"T","heading":"","quote":"..."}],"model":"m"}
            {"type":"delta","text":"안녕"}

            {"type":"delta","text":"하세요"}
            {"type":"done","assistant_message":{"message_id":"a","role":"assistant","content":"안녕하세요","status":"complete","sources":[]}}
            """;
        var h = new FakeHandler(_ => new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent(body) });
        var events = new List<ChatStreamEvent>();
        await foreach (var ev in Client(h).StreamMessageAsync("s1", new SendMessageRequest { Content = "q" }, TestContext.Current.CancellationToken))
            events.Add(ev);

        Assert.Equal(["start", "delta", "delta", "done"], events.Select(e => e.Type));
        Assert.Equal("[1] T", events[0].Sources!.Single().Label);
        Assert.Equal("안녕하세요", events[^1].AssistantMessage!.Content);
        Assert.Contains("\"stream\":true", h.Requests.Single().Body);
    }

    [Fact]
    public async Task Stream_failure_before_start_raises_llm_unavailable()
    {
        var h = new FakeHandler(_ => FakeHandler.Json(
            """{"error":{"code":"llm_unavailable","message":"ollama pull gemma3:4b","details":{"reason":"model_missing"}}}""",
            HttpStatusCode.ServiceUnavailable));
        var e = await Assert.ThrowsAsync<ApiException>(async () =>
        {
            await foreach (var _ in Client(h).StreamMessageAsync("s1", new SendMessageRequest { Content = "q" }, TestContext.Current.CancellationToken)) { }
        });
        Assert.True(e.IsLlmUnavailable);
        Assert.Equal("model_missing", e.DetailString("reason"));
    }

    [Fact]
    public async Task Connection_failure_is_reported_as_backend_unreachable()
    {
        var h = new FakeHandler(_ => throw new HttpRequestException("refused"));
        var e = await Assert.ThrowsAsync<ApiException>(() => Client(h).GetHealthAsync(TestContext.Current.CancellationToken));
        Assert.Equal("backend_unreachable", e.Code);
        Assert.Null(e.Status);
    }

    [Fact]
    public void Query_string_skips_nulls()
    {
        Assert.Equal("?a=1&c=%ED%95%9C", PawApiClient.Query(("a", "1"), ("b", null), ("c", "한")));
        Assert.Equal("", PawApiClient.Query(("b", null)));
    }
}
