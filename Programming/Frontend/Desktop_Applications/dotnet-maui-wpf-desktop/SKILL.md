---
name: dotnet-maui-wpf-desktop
description: Production architectural patterns, MVVM clean architecture, async thread synchronization, high-performance UI rendering, native interop, and memory optimization for enterprise Windows and cross-platform desktop applications using WPF, .NET MAUI, and Windows App SDK.
---

# .NET Desktop Application Architecture: WPF & MAUI

## High-Level Architecture & MVVM Pattern

Modern enterprise .NET desktop applications require clean separation of concerns, decoupling UI controls from business rules and data ingestion. 

```
+----------------------------------------------------------------------------+
|                             View Layer (XAML)                              |
|  - WPF Window / MAUI ContentPage / Controls                                |
|  - DataTemplates, Behaviors, Converters                                    |
|  - Compiled Bindings (`x:DataType` / `{Binding}`)                         |
+----------------------------------------------------------------------------+
                                     |  Two-Way Data & Command Binding
                                     v
+----------------------------------------------------------------------------+
|                     ViewModel Layer (CommunityToolkit.Mvvm)                |
|  - `ObservableObject` Properties                                           |
|  - `IAsyncRelayCommand` Execution                                          |
|  - UI State Machines, Validation (`ObservableValidator`)                   |
|  - Thread Marshalling (`MainThread` / `Dispatcher`)                        |
+----------------------------------------------------------------------------+
                                     |  Dependency Injection (`IServiceProvider`)
                                     v
+----------------------------------------------------------------------------+
|                          Core Services & Domain Model                      |
|  - Data Repositories (SQLite / EF Core)                                    |
|  - Hardware & Native OS Interop Services (P/Invoke, WinRT)                 |
|  - Background Workstreams (`IHostedService`, `Task` Pipeline)              |
+----------------------------------------------------------------------------+
```

---

## Production MVVM & Async Command Pattern

Use `CommunityToolkit.Mvvm` for clean, boilerplate-free source-generated viewmodels with full asynchronous support.

```csharp
// ViewModels/TelemetryDashboardViewModel.cs
using System;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;

namespace DesktopApp.ViewModels
{
    public record TelemetryMetric(string MetricName, double Value, DateTime Timestamp);

    public partial class TelemetryDashboardViewModel : ObservableObject
    {
        private readonly ITelemetryService _telemetryService;
        private readonly ILogger<TelemetryDashboardViewModel> _logger;

        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(RefreshTelemetryCommand))]
        private bool _isProcessing;

        [ObservableProperty]
        private string _statusMessage = "Ready";

        public ObservableCollection<TelemetryMetric> Metrics { get; } = new();

        public TelemetryDashboardViewModel(
            ITelemetryService telemetryService,
            ILogger<TelemetryDashboardViewModel> logger)
        {
            _telemetryService = telemetryService ?? throw new ArgumentNullException(nameof(telemetryService));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        private bool CanRefresh() => !IsProcessing;

        [RelayCommand(CanExecute = nameof(CanRefresh))]
        private async Task RefreshTelemetryAsync(CancellationToken cancellationToken)
        {
            IsProcessing = true;
            StatusMessage = "Fetching telemetry data...";

            try
            {
                Metrics.Clear();
                await foreach (var metric in _telemetryService.GetLiveMetricsAsync(cancellationToken))
                {
                    // ObservableCollection updates must occur on the UI Thread
                    Metrics.Add(metric);
                }

                StatusMessage = $"Updated {Metrics.Count} telemetry metrics.";
            }
            catch (OperationCanceledException)
            {
                StatusMessage = "Refresh operation cancelled.";
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load telemetry data");
                StatusMessage = "Error loading telemetry metrics.";
            }
            finally
            {
                IsProcessing = false;
            }
        }
    }
}
```

---

## Threading & UI Marshalling

In desktop applications, UI controls belong exclusively to the UI thread (WPF `Dispatcher` or MAUI `MainThread`). Executing long-running I/O or CPU operations on the UI thread freezes the app frame rate (causing "Not Responding" titlebar states).

### 1. Offloading Heavy Work & Marshalling Back
```csharp
public async Task ProcessDataPipelineAsync()
{
    // 1. Offload heavy computation to ThreadPool
    var processedData = await Task.Run(() =>
    {
        return ExecuteHeavyCrunching();
    });

    // 2. Dispatch UI update safely back to Main Thread
#if MAUI
    MainThread.BeginInvokeOnMainThread(() =>
    {
        MyObservableCollection.Add(processedData);
    });
#else
    // WPF Dispatcher
    System.Windows.Application.Current.Dispatcher.Invoke(() =>
    {
        MyObservableCollection.Add(processedData);
    });
#endif
}
```

---

## Native Interop & Secure System Storage

### 1. Secure Storage via Windows DPAPI / Native Credential Locker
Do not store API keys or connection strings in plain text configuration files.

```csharp
using System;
using System.Security.Cryptography;
using System.Text;

namespace DesktopApp.Security
{
    public static class SecureDataProtector
    {
        private static readonly byte[] Entropy = Encoding.UTF8.GetBytes("ApplicationSpecificSaltVector_9021");

        public static string ProtectString(string plainText)
        {
            if (string.IsNullOrEmpty(plainText)) return string.Empty;
            byte[] plainBytes = Encoding.UTF8.GetBytes(plainText);
            byte[] cipherBytes = ProtectedData.Protect(plainBytes, Entropy, DataProtectionScope.CurrentUser);
            return Convert.ToBase64String(cipherBytes);
        }

        public static string UnprotectString(string cipherText)
        {
            if (string.IsNullOrEmpty(cipherText)) return string.Empty;
            byte[] cipherBytes = Convert.FromBase64String(cipherText);
            byte[] plainBytes = ProtectedData.Unprotect(cipherBytes, Entropy, DataProtectionScope.CurrentUser);
            return Encoding.UTF8.GetString(plainBytes);
        }
    }
}
```

### 2. High-Performance Win32 P/Invoke Interop
```csharp
using System;
using System.Runtime.InteropServices;

namespace DesktopApp.Native
{
    public static partial class Win32Native
    {
        [LibraryImport("dwmapi.dll")]
        public static partial int DwmSetWindowAttribute(
            IntPtr hwnd,
            int dwAttribute,
            ref int pvAttribute,
            int cbAttribute);

        public const int DWMWA_USE_IMMERSIVE_DARK_MODE = 20;

        public static bool EnableDarkMode(IntPtr windowHandle, bool enabled)
        {
            int useDarkMode = enabled ? 1 : 0;
            int result = DwmSetWindowAttribute(
                windowHandle,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ref useDarkMode,
                sizeof(int));

            return result == 0;
        }
    }
}
```

---

## Performance Optimizations & Memory Management

### 1. UI Control Virtualization
When binding thousands of records in WPF `ListBox`/`DataGrid` or MAUI `CollectionView`, always ensure items container virtualization is enabled:

#### WPF XAML Virtualization Pattern:
```xml
<ListBox ItemsSource="{Binding LargeDataSet}"
         VirtualizingStackPanel.IsVirtualizing="True"
         VirtualizingStackPanel.VirtualizationMode="Recycling"
         ScrollViewer.CanContentScroll="True">
    <ListBox.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingStackPanel />
        </ItemsPanelTemplate>
    </ListBox.ItemsPanel>
</ListBox>
```

### 2. Eliminating Memory Leaks in Event Handlers & DataBindings
Desktop applications often suffer from memory leaks due to strong references maintained by event subscriptions or un-indexed `INotifyPropertyChanged` handlers.

- **Weak Messaging**: Use `WeakReferenceMessenger.Default` from CommunityToolkit to publish events without locking subscriber object lifetimes in memory.
- **Detaching Events**: Always unbind explicit C# event subscriptions (`obj.SomeEvent -= OnSomeEvent`) when closing controls/windows.
- **Compiled Bindings**: In MAUI XAML, always declare `x:DataType="viewmodels:MyViewModel"` to enable compiled bindings (`{Binding ...}`), reducing reflection overhead and lowering runtime memory consumption.

---

## Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Remediation |
| :--- | :--- | :--- |
| **`async void` Methods** | Critical | Use `async Task` everywhere except top-level event handlers; catch all unhandled exceptions inside `async void`. |
| **Blocking UI Thread via `.Result` or `.Wait()`** | High | Deadlocks UI synchronization context. Always use `await`. |
| **Direct UI Element Manipulation in ViewModel** | Medium | Violates MVVM. Use data binding (`INotifyPropertyChanged`) or Behaviors. |
| **Broad Strong Event Handlers** | High | Prevents Garbage Collector from reclaiming closed View instances. Use `WeakEventManager` or `WeakReferenceMessenger`. |
| **Un-virtualized Heavy List Controls** | High | Causes severe RAM inflation and sluggish scroll rendering for datasets > 500 items. |
