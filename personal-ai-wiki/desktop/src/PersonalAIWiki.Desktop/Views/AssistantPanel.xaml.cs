using System.Windows.Controls;
using System.Windows.Input;
using PersonalAIWiki.Core.ViewModels;

namespace PersonalAIWiki.Desktop.Views;

public partial class AssistantPanel : UserControl
{
    public AssistantPanel()
    {
        InitializeComponent();
        ChatInput.Wire(this, MessagesScroll);
    }

    private void InputBox_PreviewKeyDown(object sender, KeyEventArgs e) => ChatInput.HandleKey(DataContext as ChatViewModel, e);
}
