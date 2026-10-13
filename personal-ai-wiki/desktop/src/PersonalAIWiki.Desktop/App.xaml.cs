using System.IO;
using System.Windows;
using System.Windows.Threading;
using PersonalAIWiki.Core.Backend;
using PersonalAIWiki.Core.ViewModels;
using PersonalAIWiki.Desktop.Services;

namespace PersonalAIWiki.Desktop;

public partial class App : Application
{
    private BackendLauncher? _launcher;
    private BackendOptions _options = new();

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        DispatcherUnhandledException += OnUnhandledException;

        _options = BackendOptions.Load(Path.Combine(AppContext.BaseDirectory, "appsettings.json"));
        _launcher = new BackendLauncher(_options);
        var dialogs = new WpfDialogService();
        var vm = new MainViewModel(progress => _launcher.ConnectAsync(progress), dialogs);

        var window = new MainWindow { DataContext = vm };
        MainWindow = window;
        window.Show();
        _ = vm.InitializeAsync();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        // Stops the backend only if this app started it. The launcher never captures the UI context,
        // so blocking here cannot deadlock.
        _launcher?.DisposeAsync().AsTask().GetAwaiter().GetResult();
        base.OnExit(e);
    }

    private void OnUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
    {
        Log(e.Exception);
        new WpfDialogService().ShowError($"예기치 않은 오류가 발생했습니다.\n\n{e.Exception.Message}\n\n자세한 내용은 desktop.log 에 기록되었습니다.");
        e.Handled = true;
    }

    private void Log(Exception ex)
    {
        try
        {
            var dir = PawPaths.LogsDir(_options.ResolveDataDir());
            Directory.CreateDirectory(dir);
            File.AppendAllText(Path.Combine(dir, "desktop.log"), $"{DateTimeOffset.Now:O} {ex}\n\n");
        }
        catch
        {
            // Logging must never take the app down.
        }
    }
}
