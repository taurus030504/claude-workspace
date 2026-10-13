using System.ComponentModel;
using System.Windows;
using System.Windows.Controls;
using PersonalAIWiki.Core.Models;
using PersonalAIWiki.Core.ViewModels;

namespace PersonalAIWiki.Desktop.Views;

public partial class WikiView : UserControl
{
    private WikiViewModel? _vm;

    public WikiView()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => Attach(DataContext as WikiViewModel);
        Unloaded += (_, _) => Attach(null);
        Loaded += (_, _) => Attach(DataContext as WikiViewModel);
    }

    private void Attach(WikiViewModel? vm)
    {
        if (_vm is not null) _vm.PropertyChanged -= OnVmPropertyChanged;
        _vm = vm;
        if (_vm is null) return;
        _vm.PropertyChanged += OnVmPropertyChanged;
        ApplyLayout();
    }

    private void OnVmPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName is nameof(WikiViewModel.Mode) or nameof(WikiViewModel.IsHistoryOpen)) ApplyLayout();
    }

    /// <summary>Edit / Split / Preview column layout, plus the history column.</summary>
    private void ApplyLayout()
    {
        if (_vm is null) return;
        var mode = _vm.Mode;
        EditorColumn.Width = mode == EditorMode.Preview ? new GridLength(0) : new GridLength(1, GridUnitType.Star);
        PreviewColumn.Width = mode == EditorMode.Edit ? new GridLength(0) : new GridLength(1, GridUnitType.Star);
        SplitColumn.Width = mode == EditorMode.Split ? new GridLength(6) : new GridLength(0);
        Editor.Visibility = mode == EditorMode.Preview ? Visibility.Collapsed : Visibility.Visible;
        PreviewHost.Visibility = mode == EditorMode.Edit ? Visibility.Collapsed : Visibility.Visible;
        EditorSplitter.Visibility = mode == EditorMode.Split ? Visibility.Visible : Visibility.Collapsed;
        HistoryColumn.Width = _vm.IsHistoryOpen ? new GridLength(300) : new GridLength(0);
    }

    private async void TrashList_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (_vm is not null && e.AddedItems.Count > 0 && e.AddedItems[0] is PageSummary page)
            await _vm.OpenPageAsync(page.PageId);
    }
}
