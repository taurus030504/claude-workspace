namespace PersonalAIWiki.Core.Services;

/// <summary>UI interactions the view models need, implemented with WPF dialogs in the desktop app
/// and with a scripted fake in tests.</summary>
public interface IDialogService
{
    bool Confirm(string message, string title = "확인");
    void ShowError(string message, string title = "오류");
    void ShowInfo(string message, string title = "알림");

    /// <summary>Returns the chosen file path, or null when cancelled.</summary>
    string? PickFile(string title, string filter);

    /// <summary>Opens an http(s) link in the user's browser. Callers confirm with the user first.</summary>
    void OpenExternal(string url);

    /// <summary>Opens a local folder in Explorer.</summary>
    void OpenFolder(string path);
}

/// <summary>Navigation between screens, implemented by the main view model.</summary>
public interface INavigator
{
    void NavigateTo(string key);
    Task OpenWikiPageAsync(string pageId);
    Task OpenWikiLinkAsync(string title);
    Task ShowSearchAsync(string query);
}
