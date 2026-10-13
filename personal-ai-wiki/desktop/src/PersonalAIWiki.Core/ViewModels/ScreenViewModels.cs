using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.Services;

namespace PersonalAIWiki.Core.ViewModels;

public sealed partial class SearchViewModel : ViewModelBase
{
    private readonly IPawApi _api;
    private readonly INavigator _nav;

    public SearchViewModel(IPawApi api, INavigator nav)
    {
        _api = api;
        _nav = nav;
    }

    public ObservableCollection<SearchHit> Results { get; } = [];

    [ObservableProperty] private string _query = "";
    [ObservableProperty] private string _summary = "";

    public Task SearchAsync(string query)
    {
        Query = query;
        return RunAsync(async () =>
        {
            var r = await _api.SearchAsync(query, limit: 50);
            if (Query != query) return; // a newer search started while this one was running
            Results.Clear();
            foreach (var h in r.Items) Results.Add(h);
            Summary = r.Terms.Count == 0
                ? "검색할 단어가 없습니다. 두 글자 이상의 핵심 단어로 검색해 보세요."
                : $"'{string.Join("', '", r.Terms)}' 검색 결과 {r.Items.Count}건";
        });
    }

    [RelayCommand]
    public Task SearchAgainAsync() => SearchAsync(Query);

    [RelayCommand]
    public Task OpenResultAsync(SearchHit? hit) => hit is null ? Task.CompletedTask : _nav.OpenWikiPageAsync(hit.EntityId);
}

public sealed partial class DashboardViewModel : ViewModelBase
{
    private readonly IPawApi _api;
    private readonly INavigator _nav;

    public DashboardViewModel(IPawApi api, INavigator nav)
    {
        _api = api;
        _nav = nav;
    }

    public ObservableCollection<PageSummary> RecentPages { get; } = [];
    public ObservableCollection<TimelineEvent> RecentEvents { get; } = [];

    [ObservableProperty] private SystemStatus? _status;
    [ObservableProperty] private LlmStatus? _llm;

    [RelayCommand]
    public Task RefreshAsync() => IsBusy ? Task.CompletedTask : RunAsync(async () =>
    {
        var status = await _api.GetSystemStatusAsync();
        var llm = await _api.GetLlmStatusAsync();
        var pages = await _api.ListPagesAsync(limit: 8);
        var events = await _api.ListEventsAsync(limit: 15);
        // Update collections only after every await so overlapping refreshes cannot interleave.
        Status = status;
        Llm = llm;
        RecentPages.Clear();
        foreach (var p in pages.Items) RecentPages.Add(p);
        RecentEvents.Clear();
        foreach (var e in events.Items) RecentEvents.Add(e);
    });

    [RelayCommand]
    public Task OpenPageAsync(PageSummary? page) => page is null ? Task.CompletedTask : _nav.OpenWikiPageAsync(page.PageId);

    [RelayCommand]
    public Task OpenEventAsync(TimelineEvent? e) =>
        e is { SourceType: "wiki_page", SourceId: not null } && e.EventType != "wiki_page_deleted"
            ? _nav.OpenWikiPageAsync(e.SourceId)
            : Task.CompletedTask;
}

public sealed partial class SettingsViewModel : ViewModelBase
{
    private readonly IPawApi _api;
    private readonly IDialogService _dialogs;

    public SettingsViewModel(IPawApi api, IDialogService dialogs)
    {
        _api = api;
        _dialogs = dialogs;
    }

    public ObservableCollection<string> InstalledModels { get; } = [];
    public ObservableCollection<string> Guidance { get; } = [];

    [ObservableProperty] private LlmStatus? _llm;
    [ObservableProperty] private SystemStatus? _status;
    [ObservableProperty] private string _model = "";
    [ObservableProperty] private bool _searchWiki = true;
    [ObservableProperty] private bool _searchMemory = true;
    [ObservableProperty] private bool _searchProjects = true;
    [ObservableProperty] private bool _searchConversations;
    [ObservableProperty] private string _message = "";

    /// <summary>Raised after settings are saved so other screens can pick up the change.</summary>
    public event EventHandler? Saved;

    [RelayCommand]
    public Task RefreshAsync() => RunAsync(async () =>
    {
        var settings = await _api.GetSettingsAsync();
        Model = settings.LlmModel;
        SearchWiki = settings.SearchWiki;
        SearchMemory = settings.SearchMemory;
        SearchProjects = settings.SearchProjects;
        SearchConversations = settings.SearchConversations;
        Status = await _api.GetSystemStatusAsync();
        await CheckLlmCoreAsync();
    });

    [RelayCommand]
    public Task CheckLlmAsync() => RunAsync(CheckLlmCoreAsync);

    private async Task CheckLlmCoreAsync()
    {
        Llm = await _api.GetLlmStatusAsync();
        InstalledModels.Clear();
        foreach (var m in Llm.Models) InstalledModels.Add(m);
        Guidance.Clear();
        foreach (var g in Llm.Guidance) Guidance.Add(g);
    }

    [RelayCommand]
    public async Task SaveAsync()
    {
        var ok = await RunAsync(async () =>
        {
            await _api.UpdateSettingsAsync(new AppSettingsUpdate
            {
                LlmModel = string.IsNullOrWhiteSpace(Model) ? null : Model.Trim(),
                SearchWiki = SearchWiki,
                SearchMemory = SearchMemory,
                SearchProjects = SearchProjects,
                SearchConversations = SearchConversations,
            });
            await CheckLlmCoreAsync();
        });
        if (ok)
        {
            Message = "설정을 저장했습니다.";
            Saved?.Invoke(this, EventArgs.Empty);
        }
    }

    [RelayCommand]
    public async Task BackupAsync()
    {
        BackupResult? result = null;
        if (await RunAsync(async () => result = await _api.BackupAsync()) && result is not null)
            Message = $"백업 완료: {result.Path} ({result.SizeBytes / 1024:N0} KB)";
    }

    [RelayCommand]
    public async Task ReindexAsync()
    {
        ReindexResult? result = null;
        if (await RunAsync(async () => result = await _api.ReindexAsync()) && result is not null)
            Message = $"검색 색인을 다시 만들었습니다 (문서 {result.PagesIndexed}개).";
    }

    [RelayCommand]
    public void OpenDataFolder()
    {
        if (Status is not null) _dialogs.OpenFolder(Status.DataDir);
    }

    [RelayCommand]
    public void OpenOllamaDownload()
    {
        if (_dialogs.Confirm("브라우저에서 https://ollama.com/download 를 열까요?", "외부 링크 열기"))
            _dialogs.OpenExternal("https://ollama.com/download");
    }
}

/// <summary>Screens planned for later phases. Shown honestly as "not implemented yet".</summary>
public sealed class PlaceholderViewModel
{
    public string Title { get; init; } = "";
    public string Phase { get; init; } = "";
    public string Description { get; init; } = "";
    public IReadOnlyList<string> Planned { get; init; } = [];
}

public sealed class NavItem
{
    public string Key { get; init; } = "";
    public string Label { get; init; } = "";
    public string Glyph { get; init; } = "";
    public bool IsAvailable { get; init; } = true;
    public string? PhaseLabel { get; init; }
}
