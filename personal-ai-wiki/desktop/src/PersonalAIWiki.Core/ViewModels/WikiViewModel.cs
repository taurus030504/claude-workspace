using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.Services;

namespace PersonalAIWiki.Core.ViewModels;

public enum EditorMode
{
    Edit,
    Split,
    Preview,
}

/// <summary>Wiki screen: document tree, Markdown editor with preview, revisions, trash, import.</summary>
public sealed partial class WikiViewModel : ViewModelBase
{
    private readonly IPawApi _api;
    private readonly IDialogService _dialogs;
    private readonly INavigator _nav;
    private List<PageSummary> _allPages = [];

    public WikiViewModel(IPawApi api, IDialogService dialogs, INavigator nav)
    {
        _api = api;
        _dialogs = dialogs;
        _nav = nav;
    }

    public ObservableCollection<WikiTreeNode> Tree { get; } = [];
    public ObservableCollection<PageSummary> TrashPages { get; } = [];
    public ObservableCollection<RevisionSummary> Revisions { get; } = [];
    public ObservableCollection<SearchHit> RelatedPages { get; } = [];

    [ObservableProperty] private string _filterText = "";
    [ObservableProperty] private bool _showTrash;

    // Server state of the open document (null while editing an unsaved new page).
    [ObservableProperty] private Page? _currentPage;
    [ObservableProperty] private bool _hasDocument;

    [ObservableProperty] private string _editTitle = "";
    [ObservableProperty] private string _editFolder = "";
    [ObservableProperty] private string _editTags = "";
    [ObservableProperty] private string _editContent = "";
    [ObservableProperty] private EditorMode _mode = EditorMode.Split;
    [ObservableProperty] private string _documentStatus = "";

    [ObservableProperty] private bool _isHistoryOpen;
    [ObservableProperty] private Revision? _revisionPreview;

    public bool IsNew => HasDocument && CurrentPage is null;
    public bool IsTrashed => CurrentPage?.IsDeleted == true;
    public bool CanEdit => HasDocument && !IsTrashed;

    public bool IsDirty
    {
        get
        {
            if (!HasDocument) return false;
            if (CurrentPage is null) return EditTitle.Trim().Length > 0 || EditContent.Length > 0;
            return EditTitle.Trim() != CurrentPage.Title
                   || NormalizeFolder(EditFolder) != CurrentPage.Folder
                   || EditContent.Replace("\r\n", "\n") != CurrentPage.Content
                   || !new HashSet<string>(ParseTags(EditTags), StringComparer.OrdinalIgnoreCase).SetEquals(CurrentPage.Tags);
        }
    }

    partial void OnEditTitleChanged(string value) => EditorChanged();
    partial void OnEditFolderChanged(string value) => EditorChanged();
    partial void OnEditTagsChanged(string value) => EditorChanged();
    partial void OnEditContentChanged(string value) => EditorChanged();
    partial void OnFilterTextChanged(string value) => RebuildTree();
    partial void OnShowTrashChanged(bool value) => _ = LoadAsync();

    partial void OnCurrentPageChanged(Page? value)
    {
        OnPropertyChanged(nameof(IsNew));
        OnPropertyChanged(nameof(IsTrashed));
        OnPropertyChanged(nameof(CanEdit));
        EditorChanged();
    }

    partial void OnHasDocumentChanged(bool value)
    {
        OnPropertyChanged(nameof(IsNew));
        OnPropertyChanged(nameof(CanEdit));
        EditorChanged();
    }

    private void EditorChanged()
    {
        OnPropertyChanged(nameof(IsDirty));
        SaveCommand.NotifyCanExecuteChanged();
    }

    // ------------------------------------------------------------ list
    [RelayCommand]
    public Task LoadAsync() => RunAsync(async () =>
    {
        var active = await _api.ListPagesAsync("active");
        var trash = ShowTrash ? (await _api.ListPagesAsync("deleted")).Items : [];
        // Update collections only after every await so overlapping loads cannot interleave.
        _allPages = [.. active.Items];
        RebuildTree();
        TrashPages.Clear();
        foreach (var p in trash) TrashPages.Add(p);
    });

    public IReadOnlyList<PageSummary> AllPages => _allPages;

    private void RebuildTree()
    {
        Tree.Clear();
        foreach (var n in WikiTree.Build(_allPages, FilterText)) Tree.Add(n);
    }

    // ------------------------------------------------------------ open / new
    /// <summary>Asks before discarding unsaved edits. Returns false when the user wants to keep them.</summary>
    public bool ConfirmDiscardChanges() =>
        !IsDirty || _dialogs.Confirm("저장하지 않은 변경 사항이 있습니다. 버리고 계속할까요?", "변경 사항 버리기");

    public async Task OpenPageAsync(string pageId)
    {
        if (CurrentPage?.PageId == pageId && HasDocument) return;
        if (!ConfirmDiscardChanges()) return;
        await RunAsync(async () => Show(await _api.GetPageAsync(pageId)));
        await LoadRelatedAsync();
    }

    [RelayCommand]
    public void NewPage(string? title = null)
    {
        if (!ConfirmDiscardChanges()) return;
        CurrentPage = null;
        HasDocument = true;
        EditTitle = title ?? "";
        EditFolder = "";
        EditTags = "";
        EditContent = title is null ? "" : $"# {title}\n\n";
        Mode = EditorMode.Edit;
        DocumentStatus = "새 문서 (저장되지 않음)";
        Revisions.Clear();
        RelatedPages.Clear();
        IsHistoryOpen = false;
    }

    private void Show(Page page)
    {
        CurrentPage = page;
        HasDocument = true;
        EditTitle = page.Title;
        EditFolder = page.Folder;
        EditTags = string.Join(", ", page.Tags);
        EditContent = page.Content;
        RevisionPreview = null;
        DocumentStatus = page.IsDeleted
            ? "휴지통에 있는 문서입니다 (읽기 전용)"
            : $"리비전 {page.CurrentRevision} · {page.UpdatedAt.ToLocalTime():yyyy-MM-dd HH:mm} 수정";
        if (IsHistoryOpen) _ = LoadHistoryAsync();
        EditorChanged();
    }

    // ------------------------------------------------------------ save
    private bool CanSave() => CanEdit && IsDirty && !IsBusy && EditTitle.Trim().Length > 0;

    [RelayCommand(CanExecute = nameof(CanSave))]
    public async Task SaveAsync()
    {
        var tags = ParseTags(EditTags);
        try
        {
            IsBusy = true;
            ErrorMessage = null;
            Page saved;
            if (CurrentPage is null)
            {
                saved = await _api.CreatePageAsync(new PageCreate
                {
                    Title = EditTitle.Trim(), Content = EditContent, Folder = NormalizeFolder(EditFolder), Tags = tags,
                });
            }
            else
            {
                saved = await _api.UpdatePageAsync(CurrentPage.PageId, new PageUpdate
                {
                    ExpectedRevision = CurrentPage.CurrentRevision,
                    Title = EditTitle.Trim(),
                    Content = EditContent,
                    Folder = NormalizeFolder(EditFolder),
                    Tags = tags,
                });
            }
            Show(saved);
        }
        catch (ApiException e) when (e.IsConflict && CurrentPage is not null)
        {
            var reload = _dialogs.Confirm(
                $"이 문서는 다른 곳에서 변경되었습니다 (현재 리비전 {e.DetailInt("current_revision")}).\n\n" +
                "[예] 최신 버전을 불러옵니다. 지금 편집한 내용은 사라지므로 필요하면 먼저 복사하세요.\n" +
                "[아니요] 편집 내용을 그대로 두고 저장을 취소합니다.",
                "저장 충돌");
            if (reload) Show(await _api.GetPageAsync(CurrentPage.PageId));
            return;
        }
        catch (ApiException e)
        {
            ErrorMessage = e.Message;
            return;
        }
        finally
        {
            IsBusy = false;
            SaveCommand.NotifyCanExecuteChanged();
        }
        await LoadAsync();
        await LoadRelatedAsync();
    }

    // ------------------------------------------------------------ trash
    [RelayCommand]
    public async Task TrashAsync()
    {
        if (CurrentPage is null || IsTrashed) return;
        if (!_dialogs.Confirm($"'{CurrentPage.Title}' 문서를 휴지통으로 옮길까요?\n휴지통에서 복원할 수 있습니다.", "휴지통으로 이동")) return;
        if (await RunAsync(async () => Show(await _api.TrashPageAsync(CurrentPage.PageId)))) await LoadAsync();
    }

    [RelayCommand]
    public async Task RestoreAsync()
    {
        if (CurrentPage is null || !IsTrashed) return;
        if (await RunAsync(async () => Show(await _api.RestorePageAsync(CurrentPage.PageId)))) await LoadAsync();
    }

    [RelayCommand]
    public async Task PurgeAsync()
    {
        if (CurrentPage is null || !IsTrashed) return;
        if (!_dialogs.Confirm(
                $"'{CurrentPage.Title}' 문서를 영구 삭제합니다.\n모든 리비전, 태그, 이 문서를 인용한 기록이 함께 지워지며 되돌릴 수 없습니다.",
                "영구 삭제")) return;
        var id = CurrentPage.PageId;
        if (await RunAsync(() => _api.PurgePageAsync(id)))
        {
            CurrentPage = null;
            HasDocument = false;
            await LoadAsync();
        }
    }

    // ------------------------------------------------------------ history
    [RelayCommand]
    public async Task ToggleHistoryAsync()
    {
        IsHistoryOpen = !IsHistoryOpen;
        if (IsHistoryOpen) await LoadHistoryAsync();
        else RevisionPreview = null;
    }

    private Task LoadHistoryAsync() => RunAsync(async () =>
    {
        Revisions.Clear();
        if (CurrentPage is null) return;
        foreach (var r in await _api.ListRevisionsAsync(CurrentPage.PageId)) Revisions.Add(r);
    });

    [RelayCommand]
    public Task ViewRevisionAsync(RevisionSummary? rev) => rev is null || CurrentPage is null
        ? Task.CompletedTask
        : RunAsync(async () => RevisionPreview = await _api.GetRevisionAsync(CurrentPage.PageId, rev.RevisionNumber));

    [RelayCommand]
    public async Task RestoreRevisionAsync(RevisionSummary? rev)
    {
        if (rev is null || CurrentPage is null || IsTrashed) return;
        if (!ConfirmDiscardChanges()) return;
        if (!_dialogs.Confirm($"리비전 {rev.RevisionNumber}의 내용으로 되돌릴까요?\n현재 내용도 기록에 남아 있어 다시 되돌릴 수 있습니다.", "리비전 복원")) return;
        var page = CurrentPage;
        if (await RunAsync(async () => Show(await _api.RestoreRevisionAsync(page.PageId, rev.RevisionNumber, page.CurrentRevision))))
            await LoadAsync();
    }

    // ------------------------------------------------------------ import / links / related
    [RelayCommand]
    public async Task ImportAsync()
    {
        var path = _dialogs.PickFile("위키로 가져올 파일", "Markdown/텍스트 (*.md;*.markdown;*.txt)|*.md;*.markdown;*.txt");
        if (path is null || !ConfirmDiscardChanges()) return;
        await RunAsync(async () =>
        {
            await using var stream = File.OpenRead(path);
            Show(await _api.ImportFileAsync(Path.GetFileName(path), stream));
        });
        await LoadAsync();
    }

    [RelayCommand]
    public Task OpenLinkAsync(string? title) => string.IsNullOrWhiteSpace(title) ? Task.CompletedTask : _nav.OpenWikiLinkAsync(title);

    [RelayCommand]
    public Task OpenRelatedAsync(SearchHit? hit) => hit is null ? Task.CompletedTask : OpenPageAsync(hit.EntityId);

    private async Task LoadRelatedAsync()
    {
        RelatedPages.Clear();
        if (CurrentPage is null || CurrentPage.IsDeleted) return;
        var query = string.Join(" ", new[] { CurrentPage.Title }.Concat(CurrentPage.Tags));
        try
        {
            var result = await _api.SearchAsync(query, "wiki_page", limit: 6);
            foreach (var h in result.Items.Where(h => h.EntityId != CurrentPage.PageId).Take(5)) RelatedPages.Add(h);
        }
        catch (ApiException)
        {
            // Related documents are a convenience; failures are not worth interrupting the user.
        }
    }

    // ------------------------------------------------------------ helpers
    public static IReadOnlyList<string> ParseTags(string text) =>
        text.Split([',', ';'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(t => t.TrimStart('#').Trim())
            .Where(t => t.Length > 0)
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(t => t, StringComparer.OrdinalIgnoreCase)
            .ToList();

    public static string NormalizeFolder(string folder) =>
        string.Join("/", folder.Replace('\\', '/').Split('/', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries));
}
