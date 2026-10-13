using System.Text.Json;

namespace PersonalAIWiki.Core.Models;

public sealed class Health
{
    public string Status { get; init; } = "";
    public string App { get; init; } = "";
    public string Version { get; init; } = "";
    public int SchemaVersion { get; init; }
}

public sealed class SystemStatus
{
    public string Version { get; init; } = "";
    public string DataDir { get; init; } = "";
    public string DbPath { get; init; } = "";
    public int SchemaVersion { get; init; }
    public string FtsTokenizer { get; init; } = "";
    public int PageCount { get; init; }
    public int DeletedPageCount { get; init; }
    public int ChatSessionCount { get; init; }
    public int TimelineEventCount { get; init; }
    public bool ExternalNetworkAllowed { get; init; }
}

public sealed class LlmStatus
{
    public string Provider { get; init; } = "";
    public string BaseUrl { get; init; } = "";
    public bool Reachable { get; init; }
    public string? Version { get; init; }
    public string ConfiguredModel { get; init; } = "";
    public bool ModelAvailable { get; init; }
    public IReadOnlyList<string> Models { get; init; } = [];
    public string? Error { get; init; }
    public IReadOnlyList<string> Guidance { get; init; } = [];
}

public sealed class AppSettings
{
    public string LlmModel { get; init; } = "";
    public bool SearchWiki { get; init; } = true;
    public bool SearchMemory { get; init; } = true;
    public bool SearchProjects { get; init; } = true;
    public bool SearchConversations { get; init; }
    public IReadOnlyList<string> AvailableSearchSources { get; init; } = [];
}

public sealed class AppSettingsUpdate
{
    public string? LlmModel { get; init; }
    public bool? SearchWiki { get; init; }
    public bool? SearchMemory { get; init; }
    public bool? SearchProjects { get; init; }
    public bool? SearchConversations { get; init; }
}

public sealed class BackupResult
{
    public string Path { get; init; } = "";
    public long SizeBytes { get; init; }
}

public sealed class ReindexResult
{
    public int PagesIndexed { get; init; }
}

public sealed class TimelineEvent
{
    public string EventId { get; init; } = "";
    public string EventType { get; init; } = "";
    public string Title { get; init; } = "";
    public string Description { get; init; } = "";
    public DateTimeOffset OccurredAt { get; init; }
    public DateTimeOffset RecordedAt { get; init; }
    public string? SourceType { get; init; }
    public string? SourceId { get; init; }
    public string? ProjectId { get; init; }
    public int Importance { get; init; }
    public Dictionary<string, JsonElement> Metadata { get; init; } = [];
}

public sealed class TimelinePage
{
    public IReadOnlyList<TimelineEvent> Items { get; init; } = [];
    public string? NextCursor { get; init; }
}
