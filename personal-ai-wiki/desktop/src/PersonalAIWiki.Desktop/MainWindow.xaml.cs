using System.ComponentModel;
using System.Windows;
using System.Windows.Input;
using PersonalAIWiki.Core.ViewModels;

namespace PersonalAIWiki.Desktop;

public partial class MainWindow : Window
{
    private GridLength _rightWidth = new(370);

    public MainWindow()
    {
        InitializeComponent();
        CommandBindings.Add(new CommandBinding(ApplicationCommands.Find, (_, _) =>
        {
            GlobalSearchBox.Focus();
            GlobalSearchBox.SelectAll();
        }));
        InputBindings.Add(new KeyBinding(ApplicationCommands.Find, Key.F, ModifierKeys.Control));
    }

    private MainViewModel? Vm => DataContext as MainViewModel;

    protected override void OnClosing(CancelEventArgs e)
    {
        if (Vm is { } vm && !vm.CanClose()) e.Cancel = true;
        base.OnClosing(e);
    }

    private async void DocTree_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
    {
        if (e.NewValue is PageNode page && Vm is { } vm) await vm.OpenWikiPageAsync(page.PageId);
    }

    private void RightPanelToggle_Changed(object sender, RoutedEventArgs e)
    {
        if (RightColumn is null) return; // fires once during InitializeComponent
        if (RightPanelToggle.IsChecked == true)
        {
            RightColumn.Width = _rightWidth;
            RightSplitterColumn.Width = new GridLength(4);
            RightPanel.Visibility = Visibility.Visible;
            RightSplitter.Visibility = Visibility.Visible;
        }
        else
        {
            _rightWidth = RightColumn.Width;
            RightColumn.Width = new GridLength(0);
            RightSplitterColumn.Width = new GridLength(0);
            RightPanel.Visibility = Visibility.Collapsed;
            RightSplitter.Visibility = Visibility.Collapsed;
        }
    }
}
