using System.Text.Json;

namespace PersonalAIWiki.Core.Backend;

/// <summary>Desktop-side settings, read from appsettings.json next to the executable.
/// Data directory resolution must match backend/app/config.py.</summary>
public sealed class BackendOptions
{
    public string BaseUrl { get; set; } = "http://127.0.0.1:8765/";

    /// <summary>Overrides the data directory (same as PAW_DATA_DIR for the backend).</summary>
    public string? DataDir { get; set; }

    /// <summary>Start the backend automatically when it is not already running.</summary>
    public bool AutoStart { get; set; } = true;

    /// <summary>Folder containing the backend's <c>app</c> package. Found automatically
    /// by walking up from the executable when empty.</summary>
    public string? BackendDirectory { get; set; }

    /// <summary>Python interpreter. Defaults to the backend's .venv.</summary>
    public string? PythonExecutable { get; set; }

    public int StartupTimeoutSeconds { get; set; } = 45;

    /// <summary>Extra environment variables for a backend started by the app (e.g. PAW_OLLAMA_MODEL).</summary>
    public Dictionary<string, string> Environment { get; set; } = [];

    public static BackendOptions Load(string path)
    {
        if (!File.Exists(path)) return new BackendOptions();
        using var stream = File.OpenRead(path);
        using var doc = JsonDocument.Parse(stream, new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
        var options = doc.RootElement.TryGetProperty("Backend", out var section)
            ? section.Deserialize<BackendOptions>(new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? new BackendOptions()
            : new BackendOptions();
        // Empty strings in the file mean "use the automatic default".
        options.DataDir = NullIfBlank(options.DataDir);
        options.BackendDirectory = NullIfBlank(options.BackendDirectory);
        options.PythonExecutable = NullIfBlank(options.PythonExecutable);
        return options;
    }

    private static string? NullIfBlank(string? s) => string.IsNullOrWhiteSpace(s) ? null : s;

    public string ResolveDataDir() => PawPaths.ResolveDataDir(DataDir);

    public Uri BaseUri => new(BaseUrl.EndsWith('/') ? BaseUrl : BaseUrl + "/");
}

public static class PawPaths
{
    public const string AppDirName = "PersonalAIWiki";

    public static string ResolveDataDir(string? configured)
    {
        if (!string.IsNullOrWhiteSpace(configured)) return System.Environment.ExpandEnvironmentVariables(configured);
        var env = Environment.GetEnvironmentVariable("PAW_DATA_DIR");
        if (!string.IsNullOrWhiteSpace(env)) return env;
        if (OperatingSystem.IsWindows())
        {
            var local = Environment.GetEnvironmentVariable("LOCALAPPDATA");
            if (string.IsNullOrEmpty(local)) local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            return Path.Combine(local, AppDirName);
        }
        var xdg = Environment.GetEnvironmentVariable("XDG_DATA_HOME");
        if (string.IsNullOrEmpty(xdg)) xdg = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".local", "share");
        return Path.Combine(xdg, AppDirName);
    }

    public static string TokenPath(string dataDir) => Path.Combine(dataDir, "api_token");

    public static string LogsDir(string dataDir) => Path.Combine(dataDir, "logs");

    /// <summary>Walks up from <paramref name="start"/> looking for <c>backend/app/__init__.py</c>
    /// (the repository layout used in development and by the install script).</summary>
    public static string? FindBackendDirectory(string start)
    {
        for (var dir = new DirectoryInfo(start); dir is not null; dir = dir.Parent)
        {
            foreach (var candidate in new[] { Path.Combine(dir.FullName, "backend"), Path.Combine(dir.FullName, "personal-ai-wiki", "backend") })
            {
                if (File.Exists(Path.Combine(candidate, "app", "__init__.py"))) return candidate;
            }
        }
        return null;
    }

    public static string DefaultPython(string backendDir) =>
        OperatingSystem.IsWindows()
            ? Path.Combine(backendDir, ".venv", "Scripts", "python.exe")
            : Path.Combine(backendDir, ".venv", "bin", "python");
}

