using System.Net;
using System.Text.Json;

namespace PersonalAIWiki.Core.Api;

/// <summary>An error returned by the backend in its <c>{"error": {code, message, details}}</c> envelope,
/// or a transport failure (<see cref="Code"/> = "backend_unreachable").</summary>
public sealed class ApiException : Exception
{
    public ApiException(HttpStatusCode? status, string code, string message, JsonElement? details = null, Exception? inner = null)
        : base(message, inner)
    {
        Status = status;
        Code = code;
        Details = details;
    }

    public HttpStatusCode? Status { get; }
    public string Code { get; }
    public JsonElement? Details { get; }

    public bool IsConflict => Status == HttpStatusCode.Conflict;
    public bool IsNotFound => Status == HttpStatusCode.NotFound;
    public bool IsLlmUnavailable => Code == "llm_unavailable";

    public string? DetailString(string key) =>
        Details is { ValueKind: JsonValueKind.Object } d && d.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.String
            ? v.GetString()
            : null;

    public int? DetailInt(string key) =>
        Details is { ValueKind: JsonValueKind.Object } d && d.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.Number
            ? v.GetInt32()
            : null;

    internal static ApiException FromBody(HttpStatusCode status, string body)
    {
        try
        {
            using var doc = JsonDocument.Parse(body);
            if (doc.RootElement.TryGetProperty("error", out var err))
            {
                var code = err.TryGetProperty("code", out var c) ? c.GetString() ?? "error" : "error";
                var msg = err.TryGetProperty("message", out var m) ? m.GetString() ?? "" : "";
                JsonElement? details = err.TryGetProperty("details", out var d) ? d.Clone() : null;
                return new ApiException(status, code, msg, details);
            }
        }
        catch (JsonException)
        {
        }
        return new ApiException(status, "http_" + (int)status, string.IsNullOrWhiteSpace(body) ? status.ToString() : body);
    }
}
