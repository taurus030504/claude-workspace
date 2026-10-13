using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PersonalAIWiki.Core.Api;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.Services;

namespace PersonalAIWiki.Core.ViewModels;

public sealed partial class ChatMessageItem : ObservableObject
{
    public string Role { get; init; } = "user";
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.Now;
    public ObservableCollection<SourceRef> Sources { get; } = [];

    [ObservableProperty] private string _content = "";
    [ObservableProperty] private string _status = "complete";
    [ObservableProperty] private bool _isStreaming;
    [ObservableProperty] private string? _errorText;
    [ObservableProperty] private string? _model;

    public bool IsUser => Role == "user";
    public string RoleLabel => IsUser ? "나" : "AI";
    public bool HasSources => Sources.Count > 0;

    public void SetSources(IEnumerable<SourceRef> sources)
    {
        Sources.Clear();
        foreach (var s in sources) Sources.Add(s);
        OnPropertyChanged(nameof(HasSources));
    }

    public static ChatMessageItem From(ChatMessage m)
    {
        var item = new ChatMessageItem { Role = m.Role, CreatedAt = m.CreatedAt, Content = m.Content, Status = m.Status, Model = m.Model };
        item.SetSources(m.Sources);
        if (m.Status == "error" && m.Metadata.TryGetValue("error", out var err)) item.ErrorText = err.ToString();
        return item;
    }
}

/// <summary>AI chat with retrieval. Used full-size (with a session list) on the chat screen and
/// compact in the right-hand assistant panel.</summary>
public sealed partial class ChatViewModel : ViewModelBase
{
    private readonly IPawApi _api;
    private readonly IDialogService _dialogs;
    private readonly INavigator _nav;
    private CancellationTokenSource? _cts;
    private string? _sessionId;
    private bool _loadingSession;

    public ChatViewModel(IPawApi api, IDialogService dialogs, INavigator nav, bool compact = false)
    {
        _api = api;
        _dialogs = dialogs;
        _nav = nav;
        IsCompact = compact;
    }

    public bool IsCompact { get; }
    public ObservableCollection<ChatSession> Sessions { get; } = [];
    public ObservableCollection<ChatMessageItem> Messages { get; } = [];

    /// <summary>Sources of the latest answer, shown in the right panel.</summary>
    public ObservableCollection<SourceRef> LastSources { get; } = [];

    [ObservableProperty] private ChatSession? _selectedSession;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SendCommand))]
    private string _input = "";

    [ObservableProperty] private bool _useWiki = true;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SendCommand))]
    [NotifyCanExecuteChangedFor(nameof(CancelCommand))]
    private bool _isSending;

    /// <summary>Set when the local model is not usable; the view shows it with a link to settings.</summary>
    [ObservableProperty] private string? _llmProblem;

    public string? CurrentSessionId => _sessionId;

    public async Task InitializeAsync()
    {
        try
        {
            UseWiki = (await _api.GetSettingsAsync()).SearchWiki;
        }
        catch (ApiException)
        {
        }
        if (!IsCompact) await RefreshSessionsAsync();
    }

    [RelayCommand]
    public Task RefreshSessionsAsync() => RunAsync(async () =>
    {
        var sessions = await _api.ListSessionsAsync();
        var keep = _sessionId;
        _loadingSession = true;
        try
        {
            Sessions.Clear();
            foreach (var s in sessions) Sessions.Add(s);
            SelectedSession = Sessions.FirstOrDefault(s => s.SessionId == keep);
        }
        finally
        {
            _loadingSession = false;
        }
    });

    partial void OnSelectedSessionChanged(ChatSession? value)
    {
        if (_loadingSession || value is null || value.SessionId == _sessionId) return;
        _ = LoadSessionAsync(value.SessionId);
    }

    public Task LoadSessionAsync(string sessionId) => RunAsync(async () =>
    {
        if (IsSending) return;
        var detail = await _api.GetSessionAsync(sessionId);
        _sessionId = detail.SessionId;
        Messages.Clear();
        foreach (var m in detail.Messages) Messages.Add(ChatMessageItem.From(m));
        var lastAnswer = Messages.LastOrDefault(m => !m.IsUser);
        SetLastSources(lastAnswer?.Sources ?? []);
    });

    [RelayCommand]
    public void NewSession()
    {
        if (IsSending) return;
        _sessionId = null;
        Messages.Clear();
        SetLastSources([]);
        _loadingSession = true;
        SelectedSession = null;
        _loadingSession = false;
        LlmProblem = null;
    }

    [RelayCommand]
    public async Task DeleteSessionAsync(ChatSession? session)
    {
        if (session is null) return;
        if (!_dialogs.Confirm($"'{session.Title}' 대화를 삭제할까요? 메시지와 인용 기록이 모두 지워집니다.", "대화 삭제")) return;
        if (await RunAsync(() => _api.DeleteSessionAsync(session.SessionId)))
        {
            if (session.SessionId == _sessionId) NewSession();
            await RefreshSessionsAsync();
        }
    }

    private bool CanSend() => !IsSending && !string.IsNullOrWhiteSpace(Input);

    [RelayCommand(CanExecute = nameof(CanSend))]
    public async Task SendAsync()
    {
        var text = Input.Trim();
        Input = "";
        IsSending = true;
        LlmProblem = null;
        ErrorMessage = null;
        var user = new ChatMessageItem { Role = "user", Content = text };
        var answer = new ChatMessageItem { Role = "assistant", IsStreaming = true, Status = "streaming" };
        Messages.Add(user);
        Messages.Add(answer);
        _cts = new CancellationTokenSource();
        var createdSession = false;
        try
        {
            if (_sessionId is null)
            {
                _sessionId = (await _api.CreateSessionAsync(ct: _cts.Token)).SessionId;
                createdSession = true;
            }
            var request = new SendMessageRequest { Content = text, UseWiki = UseWiki };
            await foreach (var ev in _api.StreamMessageAsync(_sessionId, request, _cts.Token))
            {
                switch (ev.Type)
                {
                    case "start":
                        answer.Model = ev.Model;
                        answer.SetSources(ev.Sources ?? []);
                        break;
                    case "delta":
                        answer.Content += ev.Text;
                        break;
                    case "done" when ev.AssistantMessage is not null:
                        Finish(answer, ev.AssistantMessage);
                        break;
                    case "error":
                        if (ev.AssistantMessage is not null) Finish(answer, ev.AssistantMessage);
                        answer.Status = "error";
                        answer.ErrorText = ev.Message;
                        break;
                }
            }
        }
        catch (ApiException e) when (e.IsLlmUnavailable)
        {
            // Nothing was saved on the server: take the question back so the user can resend it.
            Messages.Remove(answer);
            Messages.Remove(user);
            Input = text;
            LlmProblem = e.Message;
            if (createdSession && _sessionId is not null)
            {
                // Do not leave an empty conversation behind for a question that was never asked.
                try { await _api.DeleteSessionAsync(_sessionId); } catch (ApiException) { }
                _sessionId = null;
                createdSession = false;
            }
        }
        catch (ApiException e)
        {
            answer.Status = "error";
            answer.ErrorText = e.Message;
        }
        catch (OperationCanceledException)
        {
            answer.Status = "partial";
            answer.ErrorText = "답변 생성을 중지했습니다.";
        }
        finally
        {
            answer.IsStreaming = false;
            if (answer.Status == "streaming") answer.Status = "complete";
            IsSending = false;
            _cts.Dispose();
            _cts = null;
        }
        if (!IsCompact && (createdSession || Messages.Count <= 2)) await RefreshSessionsAsync();
    }

    private void Finish(ChatMessageItem item, ChatMessage saved)
    {
        item.Content = saved.Content;
        item.Status = saved.Status;
        item.Model = saved.Model;
        item.SetSources(saved.Sources);
        SetLastSources(saved.Sources);
    }

    private void SetLastSources(IEnumerable<SourceRef> sources)
    {
        LastSources.Clear();
        foreach (var s in sources) LastSources.Add(s);
    }

    private bool CanCancel() => IsSending;

    [RelayCommand(CanExecute = nameof(CanCancel))]
    public void Cancel() => _cts?.Cancel();

    [RelayCommand]
    public Task OpenSourceAsync(SourceRef? source) =>
        source is null || source.SourceType != "wiki_page" ? Task.CompletedTask : _nav.OpenWikiPageAsync(source.SourceId);

    [RelayCommand]
    public void OpenSettings() => _nav.NavigateTo("settings");
}
