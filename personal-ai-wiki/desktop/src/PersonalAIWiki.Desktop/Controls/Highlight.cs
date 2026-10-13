using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using PersonalAIWiki.Core.Models;

namespace PersonalAIWiki.Desktop.Controls;

/// <summary>Attached property that fills a TextBlock with a search snippet, highlighting the matched spans.
/// Usage: &lt;TextBlock controls:Highlight.Hit="{Binding}" /&gt;</summary>
public static class Highlight
{
    public static readonly DependencyProperty HitProperty = DependencyProperty.RegisterAttached(
        "Hit", typeof(SearchHit), typeof(Highlight), new PropertyMetadata(null, OnHitChanged));

    public static SearchHit? GetHit(DependencyObject d) => (SearchHit?)d.GetValue(HitProperty);
    public static void SetHit(DependencyObject d, SearchHit? value) => d.SetValue(HitProperty, value);

    private static void OnHitChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is not TextBlock tb) return;
        tb.Inlines.Clear();
        if (e.NewValue is not SearchHit hit) return;
        var text = hit.Snippet;
        var brush = Application.Current?.Resources["Paw.Highlight"] as Brush ?? Brushes.DarkGoldenrod;
        var pos = 0;
        foreach (var span in hit.Highlights.Where(h => h.Length == 2).OrderBy(h => h[0]))
        {
            int start = Math.Clamp(span[0], pos, text.Length), end = Math.Clamp(span[1], start, text.Length);
            if (start > pos) tb.Inlines.Add(new Run(text[pos..start]));
            if (end > start) tb.Inlines.Add(new Run(text[start..end]) { Background = brush, FontWeight = FontWeights.SemiBold });
            pos = end;
        }
        if (pos < text.Length) tb.Inlines.Add(new Run(text[pos..]));
    }
}
