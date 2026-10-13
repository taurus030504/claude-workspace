using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Documents;
using System.Windows.Media;
using Markdig;
using Markdig.Extensions.Tables;
using Markdig.Extensions.TaskLists;
using Markdig.Syntax;
using Markdig.Syntax.Inlines;
using MdBlock = Markdig.Syntax.Block;
using MdInline = Markdig.Syntax.Inlines.Inline;
using MdTable = Markdig.Extensions.Tables.Table;
using WpfBlock = System.Windows.Documents.Block;
using WpfInline = System.Windows.Documents.Inline;
using WpfList = System.Windows.Documents.List;
using WpfTable = System.Windows.Documents.Table;

namespace PersonalAIWiki.Desktop.Markdown;

/// <summary>
/// Markdown → FlowDocument, written for untrusted content:
/// raw HTML is shown as text (never interpreted), images are not fetched (no network access
/// without consent; local attachments arrive in a later phase), and links are only reported
/// through <see cref="LinkClicked"/> so the host decides what to do.
/// [[Wiki links]] become links with the "paw-wiki:" scheme.
/// </summary>
public sealed partial class MarkdownRenderer
{
    public const string WikiScheme = "paw-wiki:";

    private static readonly MarkdownPipeline Pipeline = new MarkdownPipelineBuilder()
        .UsePipeTables()
        .UseTaskLists()
        .UseEmphasisExtras()
        .UseAutoLinks()
        .Build();

    private readonly ResourceDictionary _res;

    public MarkdownRenderer(ResourceDictionary resources) => _res = resources;

    public event Action<string>? LinkClicked;

    [GeneratedRegex(@"\[\[([^\[\]|#\n]+)(#[^\]|\n]*)?(?:\|([^\]\n]*))?\]\]")]
    private static partial Regex WikiLinkRegex();

    private Brush B(string key) => (Brush)_res[key];
    private FontFamily Mono => (FontFamily)_res["Paw.MonoFont"];

    public FlowDocument Render(string markdown)
    {
        var doc = new FlowDocument
        {
            FontFamily = (FontFamily)_res["Paw.UiFont"],
            FontSize = 14,
            Foreground = B("Paw.Text"),
            Background = Brushes.Transparent,
            TextAlignment = TextAlignment.Left,
            PagePadding = new Thickness(4, 0, 4, 16),
            LineHeight = 22,
        };
        var parsed = Markdig.Markdown.Parse(ConvertWikiLinks(markdown ?? ""), Pipeline);
        foreach (var block in parsed)
        {
            if (RenderBlock(block) is { } b) doc.Blocks.Add(b);
        }
        return doc;
    }

    /// <summary>[[Title]] / [[Title|label]] → [label](&lt;paw-wiki:Title&gt;), skipping fenced code.</summary>
    internal static string ConvertWikiLinks(string text)
    {
        var lines = text.Replace("\r\n", "\n").Split('\n');
        var inFence = false;
        for (var i = 0; i < lines.Length; i++)
        {
            var trimmed = lines[i].TrimStart();
            if (trimmed.StartsWith("```") || trimmed.StartsWith("~~~"))
            {
                inFence = !inFence;
                continue;
            }
            if (inFence || !lines[i].Contains("[[")) continue;
            lines[i] = WikiLinkRegex().Replace(lines[i], m =>
            {
                var target = m.Groups[1].Value.Trim().Replace("<", "").Replace(">", "");
                var label = m.Groups[3].Success && m.Groups[3].Value.Trim().Length > 0 ? m.Groups[3].Value.Trim() : target;
                return $"[{label}](<{WikiScheme}{target}>)";
            });
        }
        return string.Join("\n", lines);
    }

    // ------------------------------------------------------------------ blocks
    private WpfBlock? RenderBlock(MdBlock block) => block switch
    {
        HeadingBlock h => Heading(h),
        ParagraphBlock p => Para(p.Inline),
        QuoteBlock q => Quote(q),
        ListBlock l => ListOf(l),
        FencedCodeBlock or CodeBlock => Code(((LeafBlock)block).Lines.ToString()),
        HtmlBlock html => Code(html.Lines.ToString()),
        ThematicBreakBlock => new Paragraph { BorderBrush = B("Paw.Border"), BorderThickness = new Thickness(0, 0, 0, 1), Margin = new Thickness(0, 8, 0, 8), FontSize = 2 },
        MdTable t => TableOf(t),
        LinkReferenceDefinitionGroup => null,
        ContainerBlock c => SectionOf(c),
        LeafBlock leaf => Para(leaf.Inline),
        _ => null,
    };

    private Paragraph Heading(HeadingBlock h)
    {
        var p = Para(h.Inline);
        p.FontSize = h.Level switch { 1 => 26, 2 => 21, 3 => 18, 4 => 16, _ => 15 };
        p.FontWeight = FontWeights.SemiBold;
        p.Margin = new Thickness(0, h.Level <= 2 ? 18 : 12, 0, 6);
        if (h.Level <= 2)
        {
            p.BorderBrush = B("Paw.Border");
            p.BorderThickness = new Thickness(0, 0, 0, 1);
            p.Padding = new Thickness(0, 0, 0, 4);
        }
        return p;
    }

    private Paragraph Para(ContainerInline? inlines)
    {
        var p = new Paragraph { Margin = new Thickness(0, 0, 0, 10) };
        if (inlines is not null) AddInlines(p.Inlines, inlines);
        return p;
    }

    private Section SectionOf(ContainerBlock container)
    {
        var s = new Section();
        foreach (var child in container)
        {
            if (RenderBlock(child) is { } b) s.Blocks.Add(b);
        }
        return s;
    }

    private Section Quote(QuoteBlock q)
    {
        var s = SectionOf(q);
        s.BorderBrush = B("Paw.Accent");
        s.BorderThickness = new Thickness(3, 0, 0, 0);
        s.Padding = new Thickness(12, 2, 0, 2);
        s.Margin = new Thickness(0, 0, 0, 10);
        s.Foreground = B("Paw.TextMuted");
        return s;
    }

    private WpfList ListOf(ListBlock l)
    {
        var list = new WpfList
        {
            MarkerStyle = l.IsOrdered ? TextMarkerStyle.Decimal : TextMarkerStyle.Disc,
            Margin = new Thickness(0, 0, 0, 10),
            Padding = new Thickness(22, 0, 0, 0),
        };
        if (l.IsOrdered && int.TryParse(l.OrderedStart, out var start) && start > 0) list.StartIndex = start;
        foreach (var item in l)
        {
            var li = new ListItem();
            if (item is ContainerBlock c)
            {
                foreach (var child in c)
                {
                    if (RenderBlock(child) is { } b)
                    {
                        b.Margin = new Thickness(0, 0, 0, 2);
                        li.Blocks.Add(b);
                    }
                }
            }
            list.ListItems.Add(li);
        }
        return list;
    }

    private Paragraph Code(string text)
    {
        var p = new Paragraph
        {
            FontFamily = Mono,
            FontSize = 13,
            Background = B("Paw.CodeBackground"),
            Padding = new Thickness(10, 8, 10, 8),
            Margin = new Thickness(0, 0, 0, 10),
            LineHeight = 19,
        };
        var lines = text.TrimEnd('\n', '\r').Replace("\r\n", "\n").Split('\n');
        for (var i = 0; i < lines.Length; i++)
        {
            if (i > 0) p.Inlines.Add(new LineBreak());
            p.Inlines.Add(new Run(lines[i]));
        }
        return p;
    }

    private WpfTable TableOf(MdTable t)
    {
        var table = new WpfTable { CellSpacing = 0, BorderBrush = B("Paw.Border"), BorderThickness = new Thickness(1), Margin = new Thickness(0, 0, 0, 12) };
        var columns = t.OfType<Markdig.Extensions.Tables.TableRow>().Select(r => r.Count).DefaultIfEmpty(1).Max();
        for (var i = 0; i < columns; i++) table.Columns.Add(new TableColumn());
        var group = new TableRowGroup();
        foreach (var row in t.OfType<Markdig.Extensions.Tables.TableRow>())
        {
            var tr = new System.Windows.Documents.TableRow();
            if (row.IsHeader)
            {
                tr.FontWeight = FontWeights.SemiBold;
                tr.Background = B("Paw.Card");
            }
            foreach (var cell in row.OfType<Markdig.Extensions.Tables.TableCell>())
            {
                var tc = new System.Windows.Documents.TableCell { BorderBrush = B("Paw.Border"), BorderThickness = new Thickness(0, 0, 1, 1), Padding = new Thickness(8, 4, 8, 4) };
                foreach (var child in cell)
                {
                    if (RenderBlock(child) is { } b)
                    {
                        b.Margin = new Thickness(0);
                        tc.Blocks.Add(b);
                    }
                }
                tr.Cells.Add(tc);
            }
            group.Rows.Add(tr);
        }
        table.RowGroups.Add(group);
        return table;
    }

    // ------------------------------------------------------------------ inlines
    private void AddInlines(InlineCollection target, ContainerInline container)
    {
        foreach (var inline in container)
        {
            if (RenderInline(inline) is { } wpf) target.Add(wpf);
        }
    }

    private Span Children(ContainerInline container)
    {
        var span = new Span();
        AddInlines(span.Inlines, container);
        return span;
    }

    private WpfInline? RenderInline(MdInline inline)
    {
        switch (inline)
        {
            case LiteralInline lit:
                return new Run(lit.Content.ToString());
            case TaskList task:
                return new Run(task.Checked ? "☑ " : "☐ ");
            case CodeInline code:
                return new Run(code.Content) { FontFamily = Mono, Background = B("Paw.CodeBackground"), FontSize = 13 };
            case LineBreakInline lb:
                return lb.IsHard ? new LineBreak() : new Run(" ");
            case HtmlEntityInline entity:
                return new Run(entity.Transcoded.ToString());
            case HtmlInline html:
                return new Run(html.Tag) { Foreground = B("Paw.TextMuted") };
            case AutolinkInline auto:
                return auto.IsEmail ? new Run(auto.Url) : Link(new Run(auto.Url), auto.Url);
            case LinkInline { IsImage: true } image:
            {
                var alt = string.Concat(image.Descendants<LiteralInline>().Select(l => l.Content.ToString()));
                return new Run($"[이미지: {(alt.Length > 0 ? alt : image.Url)}]") { Foreground = B("Paw.TextMuted"), FontStyle = FontStyles.Italic };
            }
            case LinkInline link:
                return Link(Children(link), link.Url ?? "");
            case EmphasisInline em:
            {
                var span = Children(em);
                if (em.DelimiterChar == '~') span.TextDecorations = TextDecorations.Strikethrough;
                else if (em.DelimiterCount >= 2) span.FontWeight = FontWeights.Bold;
                else span.FontStyle = FontStyles.Italic;
                return span;
            }
            case ContainerInline container:
                return Children(container);
            default:
                return null;
        }
    }

    private Hyperlink Link(WpfInline content, string url)
    {
        var isWiki = url.StartsWith(WikiScheme, StringComparison.Ordinal);
        var link = new Hyperlink(content)
        {
            Foreground = B("Paw.Accent"),
            TextDecorations = isWiki ? null : TextDecorations.Underline,
            Cursor = System.Windows.Input.Cursors.Hand,
            ToolTip = isWiki ? $"위키 문서: {Uri.UnescapeDataString(url[WikiScheme.Length..])}" : url,
        };
        link.Click += (_, _) => LinkClicked?.Invoke(url);
        return link;
    }
}
