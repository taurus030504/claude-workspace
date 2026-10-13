using System.Diagnostics;
using PersonalAIWiki.Core.Api;

namespace PersonalAIWiki.Core.Backend;

public enum BackendState
{
    AlreadyRunning,
    Started,
    Failed,
}

public sealed record BackendConnection(BackendState State, string Message, PawApiClient? Api, string DataDir);

/// <summary>Finds the local backend or starts it as a hidden child process, then reads the
/// API token the backend writes into the data directory.</summary>
public sealed class BackendLauncher : IAsyncDisposable
{
    private readonly BackendOptions _options;
    private readonly HttpMessageHandler? _handler;
    private Process? _process;

    public BackendLauncher(BackendOptions options, HttpMessageHandler? handler = null)
    {
        _options = options;
        _handler = handler;
    }

    public bool OwnsProcess => _process is { HasExited: false };

    public async Task<BackendConnection> ConnectAsync(IProgress<string>? progress = null, CancellationToken ct = default)
    {
        var dataDir = _options.ResolveDataDir();
        progress?.Report("백엔드 확인 중…");
        if (await IsHealthyAsync(ct).ConfigureAwait(false))
            return Connect(BackendState.AlreadyRunning, "실행 중인 백엔드에 연결했습니다.", dataDir);

        if (!_options.AutoStart)
            return new BackendConnection(BackendState.Failed,
                $"백엔드({_options.BaseUrl})가 실행 중이 아닙니다. scripts\\run-backend.ps1 로 먼저 실행하세요.", null, dataDir);

        var backendDir = _options.BackendDirectory ?? PawPaths.FindBackendDirectory(AppContext.BaseDirectory);
        if (backendDir is null || !Directory.Exists(backendDir))
            return new BackendConnection(BackendState.Failed,
                "backend 폴더를 찾을 수 없습니다. appsettings.json 의 Backend:BackendDirectory 를 설정하세요.", null, dataDir);

        var python = _options.PythonExecutable ?? PawPaths.DefaultPython(backendDir);
        if (!File.Exists(python))
            return new BackendConnection(BackendState.Failed,
                $"Python 가상환경이 없습니다 ({python}). scripts\\setup.ps1 을 먼저 실행하세요.", null, dataDir);

        progress?.Report("백엔드 시작 중…");
        try
        {
            _process = StartProcess(python, backendDir, dataDir);
        }
        catch (Exception e)
        {
            return new BackendConnection(BackendState.Failed, $"백엔드를 시작하지 못했습니다: {e.Message}", null, dataDir);
        }

        var deadline = DateTime.UtcNow.AddSeconds(_options.StartupTimeoutSeconds);
        while (DateTime.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            if (_process.HasExited)
                return new BackendConnection(BackendState.Failed,
                    $"백엔드가 시작 직후 종료되었습니다 (코드 {_process.ExitCode}). 로그: {Path.Combine(PawPaths.LogsDir(dataDir), "backend.log")}",
                    null, dataDir);
            if (await IsHealthyAsync(ct).ConfigureAwait(false))
                return Connect(BackendState.Started, "백엔드를 시작했습니다.", dataDir);
            await Task.Delay(400, ct).ConfigureAwait(false);
        }
        return new BackendConnection(BackendState.Failed, "백엔드 시작 시간이 초과되었습니다. backend.log 를 확인하세요.", null, dataDir);
    }

    private BackendConnection Connect(BackendState state, string message, string dataDir)
    {
        var tokenPath = PawPaths.TokenPath(dataDir);
        if (!File.Exists(tokenPath))
            return new BackendConnection(BackendState.Failed,
                $"API 토큰 파일이 없습니다 ({tokenPath}). 백엔드와 앱이 같은 데이터 폴더를 쓰는지 확인하세요.", null, dataDir);
        var token = File.ReadAllText(tokenPath).Trim();
        return new BackendConnection(state, message, new PawApiClient(_options.BaseUri, token, _handler), dataDir);
    }

    private Process StartProcess(string python, string backendDir, string dataDir)
    {
        var psi = new ProcessStartInfo(python, "-m app")
        {
            WorkingDirectory = backendDir,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = false,
            RedirectStandardError = false,
        };
        psi.Environment["PAW_DATA_DIR"] = dataDir;
        psi.Environment["PAW_PORT"] = _options.BaseUri.Port.ToString();
        psi.Environment["PYTHONUTF8"] = "1";
        foreach (var (key, value) in _options.Environment) psi.Environment[key] = value;
        return Process.Start(psi) ?? throw new InvalidOperationException("Process.Start returned null");
    }

    private async Task<bool> IsHealthyAsync(CancellationToken ct)
    {
        using var http = _handler is null ? new HttpClient() : new HttpClient(_handler, disposeHandler: false);
        http.Timeout = TimeSpan.FromSeconds(2);
        try
        {
            using var resp = await http.GetAsync(new Uri(_options.BaseUri, "api/v1/health"), ct).ConfigureAwait(false);
            return resp.IsSuccessStatusCode;
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException && !ct.IsCancellationRequested)
        {
            return false;
        }
    }

    /// <summary>Stops the backend only if this launcher started it (graceful, then forced).</summary>
    public async ValueTask DisposeAsync()
    {
        if (_process is null || _process.HasExited) return;
        try
        {
            var tokenPath = PawPaths.TokenPath(_options.ResolveDataDir());
            if (File.Exists(tokenPath))
            {
                using var api = new PawApiClient(_options.BaseUri, File.ReadAllText(tokenPath).Trim(), _handler);
                await api.ShutdownAsync().ConfigureAwait(false);
            }
            using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(8));
            await _process.WaitForExitAsync(cts.Token).ConfigureAwait(false);
        }
        catch
        {
            // Fall through to a forced stop. SQLite transactions keep the database consistent either way.
        }
        if (!_process.HasExited) _process.Kill(entireProcessTree: true);
        _process.Dispose();
    }
}
