namespace PersonalAIWiki.Core.Models;

// DTOs mirror backend/app/schemas/*.py. JSON uses snake_case (see PawJson).

public sealed class PageSummary
{
    public string PageId { get; init; } = "";
    public string Title { get; init; } = "";
    public string Folder { get; init; } = "";
    public IReadOnlyList<string> Tags { get; init; } = [];
    public string Excerpt { get; init; } = "";
    public string SourceType { get; init; } = "user";
    public int CurrentRevision { get; init; }
    public string Status { get; init; } = "active";
    public int ContentLength { get; init; }
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset UpdatedAt { get; init; }
    public DateTimeOffset? DeletedAt { get; init; }
}

public sealed class Page
{
    public string PageId { get; init; } = "";
    public string Title { get; init; } = "";
    public string Folder { get; init; } = "";
    public string Content { get; init; } = "";
    public IReadOnlyList<string> Tags { get; init; } = [];
    public string? Summary { get; init; }
    public string SourceType { get; init; } = "user";
    public string? SourceRef { get; init; }
    public int CurrentRevision { get; init; }
    public string Status { get; init; } = "active";
    public IReadOnlyList<string> Links { get; init; } = [];
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset UpdatedAt { get; init; }
    public DateTimeOffset? DeletedAt { get; init; }

    public bool IsDeleted => Status == "deleted";
}

public sealed class PageList
{
    public IReadOnlyList<PageSummary> Items { get; init; } = [];
    public int Total { get; init; }
}

public sealed class PageCreate
{
    public string Title { get; init; } = "";
    public string Content { get; init; } = "";
    public string Folder { get; init; } = "";
    public IReadOnlyList<string> Tags { get; init; } = [];
    public string? ChangeNote { get; init; }
}

/// <summary>Partial update; null fields are left unchanged (omitted from JSON).</summary>
public sealed class PageUpdate
{
    public int ExpectedRevision { get; init; }
    public string? Title { get; init; }
    public string? Content { get; init; }
    public string? Folder { get; init; }
    public IReadOnlyList<string>? Tags { get; init; }
    public string? ChangeNote { get; init; }
}

public sealed class RevisionSummary
{
    public string RevisionId { get; init; } = "";
    public int RevisionNumber { get; init; }
    public string Title { get; init; } = "";
    public string Folder { get; init; } = "";
    public string? ChangeNote { get; init; }
    public string Author { get; init; } = "user";
    public int ContentLength { get; init; }
    public DateTimeOffset CreatedAt { get; init; }
}

public sealed class Revision
{
    public string RevisionId { get; init; } = "";
    public string PageId { get; init; } = "";
    public int RevisionNumber { get; init; }
    public string Title { get; init; } = "";
    public string Folder { get; init; } = "";
    public string Content { get; init; } = "";
    public string? ChangeNote { get; init; }
    public string Author { get; init; } = "user";
    public DateTimeOffset CreatedAt { get; init; }
}

public sealed class FolderInfo
{
    public string Folder { get; init; } = "";
    public int PageCount { get; init; }
}

public sealed class TagInfo
{
    public string Name { get; init; } = "";
    public int Usage { get; init; }
}

public sealed class SearchHit
{
    public string EntityType { get; init; } = "";
    public string EntityId { get; init; } = "";
    public string? ChunkId { get; init; }
    public string Title { get; init; } = "";
    public string Heading { get; init; } = "";
    public string Snippet { get; init; } = "";
    public IReadOnlyList<int[]> Highlights { get; init; } = [];
    public IReadOnlyList<string> MatchedTerms { get; init; } = [];
    public double Score { get; init; }
}

public sealed class SearchResponse
{
    public string Query { get; init; } = "";
    public IReadOnlyList<string> Terms { get; init; } = [];
    public string Tokenizer { get; init; } = "";
    public IReadOnlyList<SearchHit> Items { get; init; } = [];
}
