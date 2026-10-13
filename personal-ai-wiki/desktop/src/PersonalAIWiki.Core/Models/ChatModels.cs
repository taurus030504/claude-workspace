using System.Text.Json;

namespace PersonalAIWiki.Core.Models;

public sealed class ChatSession
{
    public string SessionId { get; init; } = "";
    public string Title { get; init; } = "";
    public string Origin { get; init; } = "app";
    public string? SourceService { get; init; }
    public string? Model { get; init; }
    public int MessageCount { get; init; }
    public DateTimeOffset StartedAt { get; init; }
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset UpdatedAt { get; init; }
}

public sealed class SourceRef
{
    public int Number { get; init; }
    public string SourceType { get; init; } = "";
    public string SourceId { get; init; } = "";
    public string Title { get; init; } = "";
    public string Heading { get; init; } = "";
    public string Quote { get; init; } = "";
    public string? ChunkId { get; init; }
    public int? Revision { get; init; }
    public bool Cited { get; init; }

    public string Label => string.IsNullOrEmpty(Heading) ? $"[{Number}] {Title}" : $"[{Number}] {Title} › {Heading}";
}

public sealed class ChatMessage
{
    public string MessageId { get; init; } = "";
    public string SessionId { get; init; } = "";
    public int Seq { get; init; }
    public string Role { get; init; } = "";
    public string Content { get; init; } = "";
    public string? Model { get; init; }
    public string Status { get; init; } = "complete";
    public DateTimeOffset CreatedAt { get; init; }
    public IReadOnlyList<SourceRef> Sources { get; init; } = [];
    public Dictionary<string, JsonElement> Metadata { get; init; } = [];
}

public sealed class ChatSessionDetail
{
    public string SessionId { get; init; } = "";
    public string Title { get; init; } = "";
    public string? Model { get; init; }
    public IReadOnlyList<ChatMessage> Messages { get; init; } = [];
}

public sealed class SendMessageRequest
{
    public string Content { get; init; } = "";
    public bool Stream { get; init; } = true;
    public string? Model { get; init; }
    public bool? UseWiki { get; init; }
}

/// <summary>One NDJSON line of a streamed answer: start, delta, done or error.</summary>
public sealed class ChatStreamEvent
{
    public string Type { get; init; } = "";
    public ChatMessage? UserMessage { get; init; }
    public IReadOnlyList<SourceRef>? Sources { get; init; }
    public string? Model { get; init; }
    public string? Text { get; init; }
    public ChatMessage? AssistantMessage { get; init; }
    public string? Code { get; init; }
    public string? Message { get; init; }
}
