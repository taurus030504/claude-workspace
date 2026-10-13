using CommunityToolkit.Mvvm.ComponentModel;
using PersonalAIWiki.Core.Api;

namespace PersonalAIWiki.Core.ViewModels;

public abstract partial class ViewModelBase : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private string? _errorMessage;

    /// <summary>Runs a backend call with the busy flag set; API errors become <see cref="ErrorMessage"/>.</summary>
    protected async Task<bool> RunAsync(Func<Task> action)
    {
        IsBusy = true;
        ErrorMessage = null;
        try
        {
            await action();
            return true;
        }
        catch (ApiException e)
        {
            ErrorMessage = e.Message;
            return false;
        }
        finally
        {
            IsBusy = false;
        }
    }
}
