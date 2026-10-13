using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Backend;
using PersonalAIWiki.Core.Services;

namespace PersonalAIWiki.Core.ViewModels;

/// <summary>Shell: connection to the backend, navigation, global search, status bar.</summary>
public sealed partial class MainViewModel : ObservableObject, INavigator
{
    private readonly Func<IProgress<string>, Task<BackendConnection>> _connect;
    private readonly IDialogService _dialogs;
    private readonly Dictionary<string, PlaceholderViewModel> _placeholders;
    private bool _navigating;

    public MainViewModel(Func<IProgress<string>, Task<BackendConnection>> connect, IDialogService dialogs)
    {
        _connect = connect;
        _dialogs = dialogs;
        NavItems =
        [
            new NavItem { Key = "dashboard", Label = "대시보드", Glyph = "\uE80F" },
            new NavItem { Key = "wiki", Label = "위키", Glyph = "\uE8F1" },
            new NavItem { Key = "chat", Label = "AI 채팅", Glyph = "\uE8BD" },
            new NavItem { Key = "memory", Label = "메모리", Glyph = "\uE7BE", IsAvailable = false, PhaseLabel = "Phase 1" },
            new NavItem { Key = "projects", Label = "프로젝트", Glyph = "\uE8FD", IsAvailable = false, PhaseLabel = "Phase 2" },
            new NavItem { Key = "timeline", Label = "타임라인", Glyph = "\uE81C", IsAvailable = false, PhaseLabel = "Phase 4" },
            new NavItem { Key = "graph", Label = "지식 그래프", Glyph = "\uE8B9", IsAvailable = false, PhaseLabel = "Phase 5" },
            new NavItem { Key = "import", Label = "대화 가져오기", Glyph = "\uE8B5", IsAvailable = false, PhaseLabel = "Phase 3" },
            new NavItem { Key = "settings", Label = "설정", Glyph = "\uE713" },
        ];
        _placeholders = new()
        {
            ["memory"] = new() { Title = "AI 메모리", Phase = "Phase 1에서 구현 예정", Description = "대화에서 추출한 기억 후보를 사용자가 승인한 것만 장기 기억으로 저장합니다.",
                Planned = ["메모리 유형 분류 (프로필, 선호, 목표, 결정 등)", "AI 기억 후보 추출 → 사용자 승인", "출처 연결과 충돌 비교", "메모리 기반 질의응답"] },
            ["projects"] = new() { Title = "프로젝트", Phase = "Phase 2에서 구현 예정", Description = "프로젝트와 작업을 관리하고, 관련 위키·메모리·대화를 연결합니다.",
                Planned = ["프로젝트/작업 CRUD, 상태·우선순위", "작업 기반 진행률", "프로젝트 대시보드", "활동 타임라인 이벤트 자동 기록"] },
            ["timeline"] = new() { Title = "메모리 타임라인", Phase = "Phase 4에서 화면 구현 예정", Description = "이벤트 기록은 지금부터 수집 중입니다 (대시보드의 '최근 활동'에서 확인 가능).",
                Planned = ["일/월/년 보기", "프로젝트·유형 필터", "중요 이벤트 강조", "이벤트에서 문서·작업으로 이동"] },
            ["graph"] = new() { Title = "지식 그래프", Phase = "Phase 5에서 구현 예정", Description = "문서, 메모리, 프로젝트, 작업, 대화 사이의 관계를 시각화합니다.",
                Planned = ["노드 드래그·확대·이동", "프로젝트 중심 부분 로딩", "관계 추가/삭제", "AI 제안 관계와 확정 관계 구분"] },
            ["import"] = new() { Title = "AI 대화 가져오기", Phase = "Phase 3에서 구현 예정", Description = "ChatGPT 등에서 내보낸 대화를 원본 그대로 보존하며 가져옵니다. (Markdown/텍스트 파일을 위키 문서로 가져오는 기능은 위키 화면에서 지금 사용할 수 있습니다.)",
                Planned = ["형식 감지와 미리보기", "중복 검사", "선택한 대화만 가져오기", "요약과 지식·메모리 후보 생성 (승인 후 반영)"] },
        };
    }

    public ObservableCollection<NavItem> NavItems { get; }

    [ObservableProperty] private NavItem? _selectedNav;
    [ObservableProperty] private object? _currentView;
    [ObservableProperty] private bool _isConnected;
    [ObservableProperty] private bool _isConnecting;
    [ObservableProperty] private string _connectionMessage = "백엔드에 연결하는 중…";
    [ObservableProperty] private string _llmStatusText = "LLM 확인 전";
    [ObservableProperty] private bool _llmReady;
    [ObservableProperty] private string _globalQuery = "";
    [ObservableProperty] private string? _dataDir;

    public IPawApi? Api { get; private set; }
    public DashboardViewModel? Dashboard { get; private set; }
    public WikiViewModel? Wiki { get; private set; }
    public ChatViewModel? Chat { get; private set; }
    public ChatViewModel? Assistant { get; private set; }
    public SearchViewModel? Search { get; private set; }
    public SettingsViewModel? Settings { get; private set; }

    public bool IsWikiActive => ReferenceEquals(CurrentView, Wiki) && Wiki is not null;

    partial void OnCurrentViewChanged(object? value) => OnPropertyChanged(nameof(IsWikiActive));

    [RelayCommand]
    public async Task InitializeAsync()
    {
        if (IsConnecting) return;
        IsConnecting = true;
        IsConnected = false;
        try
        {
            var progress = new Progress<string>(m => ConnectionMessage = m);
            var connection = await _connect(progress);
            DataDir = connection.DataDir;
            ConnectionMessage = connection.Message;
            if (connection.Api is null) return;
            Attach(connection.Api);
            IsConnected = true;
            NavigateTo("dashboard");
            // The dashboard refreshes itself when NavigateTo shows it.
            await Task.WhenAll(Wiki!.LoadAsync(), Chat!.InitializeAsync(), Assistant!.InitializeAsync());
            await RefreshLlmStatusAsync();
        }
        finally
        {
            IsConnecting = false;
        }
    }

    /// <summary>Wires the screens to an API client (separate from InitializeAsync so tests can inject a fake).</summary>
    public void Attach(IPawApi api)
    {
        Api = api;
        Dashboard = new DashboardViewModel(api, this);
        Wiki = new WikiViewModel(api, _dialogs, this);
        Chat = new ChatViewModel(api, _dialogs, this);
        Assistant = new ChatViewModel(api, _dialogs, this, compact: true);
        Search = new SearchViewModel(api, this);
        Settings = new SettingsViewModel(api, _dialogs);
        Settings.Saved += async (_, _) =>
        {
            await RefreshLlmStatusAsync();
            await Chat.InitializeAsync();
            await Assistant.InitializeAsync();
        };
        OnPropertyChanged(string.Empty);
    }

    [RelayCommand]
    public async Task RefreshLlmStatusAsync()
    {
        if (Api is null) return;
        try
        {
            var s = await Api.GetLlmStatusAsync();
            LlmReady = s.Reachable && s.ModelAvailable;
            LlmStatusText = !s.Reachable ? "LLM: Ollama 연결 안 됨"
                : !s.ModelAvailable ? $"LLM: '{s.ConfiguredModel}' 모델 없음"
                : $"LLM: {s.ConfiguredModel}";
        }
        catch (ApiException e)
        {
            LlmReady = false;
            LlmStatusText = "LLM 상태 확인 실패: " + e.Message;
        }
    }

    partial void OnSelectedNavChanged(NavItem? value)
    {
        if (value is null || _navigating) return;
        NavigateTo(value.Key);
    }

    public void NavigateTo(string key)
    {
        if (!IsConnected && key != "settings") return;
        _navigating = true;
        try
        {
            SelectedNav = NavItems.FirstOrDefault(n => n.Key == key);
        }
        finally
        {
            _navigating = false;
        }
        CurrentView = key switch
        {
            "dashboard" => Dashboard,
            "wiki" => Wiki,
            "chat" => Chat,
            "settings" => Settings,
            _ when _placeholders.TryGetValue(key, out var p) => p,
            _ => Dashboard,
        };
        switch (CurrentView)
        {
            case DashboardViewModel d: _ = d.RefreshAsync(); break;
            case SettingsViewModel s: _ = s.RefreshAsync(); break;
        }
    }

    public async Task OpenWikiPageAsync(string pageId)
    {
        if (Wiki is null) return;
        NavigateTo("wiki");
        await Wiki.OpenPageAsync(pageId);
    }

    public async Task OpenWikiLinkAsync(string title)
    {
        if (Api is null || Wiki is null) return;
        var page = await Api.ResolveTitleAsync(title);
        if (page is not null)
        {
            await OpenWikiPageAsync(page.PageId);
        }
        else if (_dialogs.Confirm($"'{title}' 문서가 아직 없습니다. 새로 만들까요?", "새 문서"))
        {
            NavigateTo("wiki");
            Wiki.NewPage(title);
        }
    }

    public async Task ShowSearchAsync(string query)
    {
        if (Search is null || string.IsNullOrWhiteSpace(query)) return;
        _navigating = true;
        SelectedNav = null;
        _navigating = false;
        CurrentView = Search;
        await Search.SearchAsync(query.Trim());
    }

    [RelayCommand]
    public Task GlobalSearchAsync() => ShowSearchAsync(GlobalQuery);

    [RelayCommand]
    public void NewPage()
    {
        if (Wiki is null) return;
        NavigateTo("wiki");
        Wiki.NewPage();
    }

    /// <summary>Called when the window is closing. Returns false to keep it open.</summary>
    public bool CanClose() => Wiki?.ConfirmDiscardChanges() ?? true;
}
