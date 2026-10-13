using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using PersonalAIWiki.Core.Models;

namespace PersonalAIWiki.Core.ViewModels;

public abstract class WikiTreeNode : ObservableObject
{
    public string Name { get; init; } = "";
}

public sealed partial class FolderNode : WikiTreeNode
{
    public string Path { get; init; } = "";
    public ObservableCollection<WikiTreeNode> Children { get; } = [];

    [ObservableProperty]
    private bool _isExpanded = true;

    public int PageCount => Children.Sum(c => c is FolderNode f ? f.PageCount : 1);
}

public sealed class PageNode : WikiTreeNode
{
    public PageSummary Summary { get; init; } = new();
    public string PageId => Summary.PageId;
}

public static class WikiTree
{
    /// <summary>Builds a folder tree from page folders ("게임/설계"). Folders come before pages,
    /// both sorted by name. A non-empty <paramref name="filter"/> keeps pages whose title,
    /// folder or tags contain it.</summary>
    public static List<WikiTreeNode> Build(IEnumerable<PageSummary> pages, string? filter = null)
    {
        var root = new FolderNode { Name = "", Path = "" };
        var folders = new Dictionary<string, FolderNode>(StringComparer.OrdinalIgnoreCase) { [""] = root };
        var f = filter?.Trim();

        foreach (var page in pages)
        {
            if (!string.IsNullOrEmpty(f)
                && !page.Title.Contains(f, StringComparison.OrdinalIgnoreCase)
                && !page.Folder.Contains(f, StringComparison.OrdinalIgnoreCase)
                && !page.Tags.Any(t => t.Contains(f, StringComparison.OrdinalIgnoreCase)))
                continue;
            GetFolder(folders, page.Folder).Children.Add(new PageNode { Name = page.Title, Summary = page });
        }

        Sort(root);
        return [.. root.Children];
    }

    private static FolderNode GetFolder(Dictionary<string, FolderNode> folders, string path)
    {
        if (folders.TryGetValue(path, out var existing)) return existing;
        var slash = path.LastIndexOf('/');
        var parent = GetFolder(folders, slash < 0 ? "" : path[..slash]);
        var node = new FolderNode { Name = slash < 0 ? path : path[(slash + 1)..], Path = path };
        parent.Children.Add(node);
        folders[path] = node;
        return node;
    }

    private static void Sort(FolderNode folder)
    {
        var sorted = folder.Children
            .OrderBy(n => n is FolderNode ? 0 : 1)
            .ThenBy(n => n.Name, StringComparer.CurrentCultureIgnoreCase)
            .ToList();
        folder.Children.Clear();
        foreach (var n in sorted)
        {
            folder.Children.Add(n);
            if (n is FolderNode sub) Sort(sub);
        }
    }
}
