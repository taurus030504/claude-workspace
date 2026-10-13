using System.Collections.Specialized;
using System.Windows.Controls;
using System.Windows.Input;
using PersonalAIWiki.Core.ViewModels;

namespace PersonalAIWiki.Desktop.Views;

public partial class ChatView : UserControl
{
    public ChatView()
    {
        InitializeComponent();
        ChatInput.Wire(this, MessagesScroll);
    }

    private void InputBox_PreviewKeyDown(object sender, KeyEventArgs e) => ChatInput.HandleKey(DataContext as ChatViewModel, e);
}

/// <summary>Shared behaviour of the full chat view and the compact assistant panel.</summary>
internal static class ChatInput
{
    /// <summary>Enter sends, Shift+Enter inserts a line break.</summary>
    public static void HandleKey(ChatViewModel? vm, KeyEventArgs e)
    {
        if (vm is null || e.Key != Key.Enter || Keyboard.Modifiers.HasFlag(ModifierKeys.Shift)) return;
        e.Handled = true;
        if (vm.SendCommand.CanExecute(null)) vm.SendCommand.Execute(null);
    }

    /// <summary>Keeps the message list scrolled to the newest message while answers stream in.</summary>
    public static void Wire(UserControl view, ScrollViewer scroll)
    {
        ChatViewModel? current = null;

        void OnMessages(object? s, NotifyCollectionChangedEventArgs e)
        {
            scroll.ScrollToEnd();
            if (e.NewItems is null) return;
            foreach (ChatMessageItem item in e.NewItems)
                item.PropertyChanged += (_, a) =>
                {
                    if (a.PropertyName == nameof(ChatMessageItem.Content)) scroll.ScrollToEnd();
                };
        }

        view.DataContextChanged += (_, _) =>
        {
            if (current is not null) current.Messages.CollectionChanged -= OnMessages;
            current = view.DataContext as ChatViewModel;
            if (current is not null) current.Messages.CollectionChanged += OnMessages;
        };
    }
}
