using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Threading;
using PersonalAIWiki.Desktop.Markdown;
using PersonalAIWiki.Desktop.Services;

namespace PersonalAIWiki.Desktop.Controls;

/// <summary>Read-only Markdown preview. Re-renders 250 ms after the text stops changing so typing
/// in a long document stays responsive. Wiki links go to <see cref="WikiLinkCommand"/>;
/// web links open in the browser only after the user confirms.</summary>
public sealed class MarkdownViewer : FlowDocumentScrollViewer
{
    public static readonly DependencyProperty MarkdownProperty = DependencyProperty.Register(
        nameof(Markdown), typeof(string), typeof(MarkdownViewer), new PropertyMetadata("", (d, _) => ((MarkdownViewer)d).Schedule()));

    public static readonly DependencyProperty WikiLinkCommandProperty = DependencyProperty.Register(
        nameof(WikiLinkCommand), typeof(ICommand), typeof(MarkdownViewer));

    private readonly DispatcherTimer _timer;
    private MarkdownRenderer? _renderer;

    public MarkdownViewer()
    {
        VerticalScrollBarVisibility = ScrollBarVisibility.Auto;
        HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled;
        IsToolBarVisible = false;
        Focusable = true;
        _timer = new DispatcherTimer(TimeSpan.FromMilliseconds(250), DispatcherPriority.Background, (_, _) => RenderNow(), Dispatcher);
        _timer.Stop();
        Loaded += (_, _) => RenderNow();
    }

    public string Markdown
    {
        get => (string)GetValue(MarkdownProperty);
        set => SetValue(MarkdownProperty, value);
    }

    public ICommand? WikiLinkCommand
    {
        get => (ICommand?)GetValue(WikiLinkCommandProperty);
        set => SetValue(WikiLinkCommandProperty, value);
    }

    private void Schedule()
    {
        _timer.Stop();
        _timer.Start();
    }

    private void RenderNow()
    {
        _timer.Stop();
        if (!IsLoaded) return;
        if (_renderer is null)
        {
            _renderer = new MarkdownRenderer(Application.Current.Resources);
            _renderer.LinkClicked += OnLinkClicked;
        }
        Document = _renderer.Render(Markdown ?? "");
    }

    private void OnLinkClicked(string url)
    {
        if (url.StartsWith(MarkdownRenderer.WikiScheme, StringComparison.Ordinal))
        {
            var title = Uri.UnescapeDataString(url[MarkdownRenderer.WikiScheme.Length..]);
            if (WikiLinkCommand?.CanExecute(title) == true) WikiLinkCommand.Execute(title);
            return;
        }
        if (!Uri.TryCreate(url, UriKind.Absolute, out var uri) || (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
        {
            // file:, javascript:, relative paths etc. from document content are never opened.
            return;
        }
        var dialogs = new WpfDialogService();
        if (dialogs.Confirm($"외부 링크를 브라우저에서 열까요?\n\n{uri.AbsoluteUri}", "외부 링크"))
            dialogs.OpenExternal(uri.AbsoluteUri);
    }
}
