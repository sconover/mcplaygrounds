using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Diagnostics;
using System.Threading;
using mcprog2.Util;
using System.Windows.Input;
using System.Runtime.InteropServices;
using CefSharp.Wpf;
using System.Windows.Interop;
using System.Windows.Media;
using Newtonsoft.Json.Schema;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Diagnostics.Contracts;
using Microsoft.VisualBasic;
using System.Threading.Tasks;
using Microsoft.VisualBasic.Logging;

namespace mcprog2
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private UIProcessUtil.DockedWindowAndSubProcess dockedWindowAndSubProcess;
        private SynchronizationContext syncContext;
        private GlobalKeyHook f12ToggleKeyHook;
        private bool focusToggle;
        private JObject config;
        private string lastBrowserUrlFromConfig;

        public MainWindow()
        {
            InitializeComponent();

            syncContext = SynchronizationContext.Current;
            Trace.Listeners.Add(LogUtil.getAppLogTraceListener());

            AppDomain.CurrentDomain.UnhandledException += (object sender, UnhandledExceptionEventArgs args) =>
            {
                Exception ex = (Exception)args.ExceptionObject;
                Trace.TraceError(ex.Message + "\ntrace: " + ex.StackTrace.Trim());
                throw ex;
            };
        }
        
        private void HostedAppWindow_Loaded(object sender, RoutedEventArgs e)
        {
            this.Title = "Launching, Please Wait...";

            GlobalSettings.loadFromSystemEnvironment();

            f12ToggleKeyHook = new GlobalKeyHook(System.Windows.Forms.Keys.F12, toggleFocus);
            f12ToggleKeyHook.startListeningForKeyPress();

            HostedAppWindow.SizeChanged += new SizeChangedEventHandler(HostedAppWindow_Resize);

            this.Closing += (innerSender, args) => shutdown();

            this.config = ConfigUtil.load();
            GlobalSettings.loadFromJsonConfig(this.config);

            Browser.WebBrowser.RequestHandler = ConfigUtil.loadBasicAuthPopulatorFromBootstrapJson();
            Browser.WebBrowser.LifeSpanHandler = new BrowserLifeSpanHandler();
            lastBrowserUrlFromConfig = (string)config["browser_window"]["url"];
            loadUrlInBrowser(lastBrowserUrlFromConfig); 
            // do not use Browser.WebBrowser.Load ... things do not load properly when using buildt exe's

            extractNativeJars();

            startAndDockHostedApp();
            focusOnHostedAppWindow();
            updateWindowTitle();

            Task.Run(() => checkForNewBrowserUrlEverySeconds(10));
        }

        private void updateWindowTitle()
        {
            this.Title = hostedAppName() + " | " + (string)config["browser_window"]["url"];
        }

        private void checkForNewBrowserUrlEverySeconds(int secondsBetweenChecks)
        {
            while (true)
            {
                try
                {
                    string currentUrl = ConfigUtil.getLatestBrowserUrlFromConfig();
                    if (currentUrl != lastBrowserUrlFromConfig)
                    {
                        log("detected new url from config, automatically loading in browser. new='" + currentUrl + "' old='" + lastBrowserUrlFromConfig + "'");
                        loadUrlInBrowser(currentUrl);
                        lastBrowserUrlFromConfig = currentUrl;
                    }
                } catch (Exception ex)
                {
                    log("while polling for new browser url, caught exception: " + ex.ToString());
                }

                Thread.Sleep(secondsBetweenChecks * 1000);
            }
        }

        private void HostedAppWindow_Resize(object sender, EventArgs e)
        {
            UIProcessUtil.MakeWindowSameSizeAndPositionAsElement(
                this, 
                dockedWindowAndSubProcess.dockedWindowHandle, 
                HostedAppWindow, 
                (int)HostedAppWindow.BorderThickness.Top);
        }

        private void Window_KeyDown(object sender, KeyEventArgs e)
        {
            if (Keyboard.IsKeyDown(Key.LeftAlt) && Keyboard.IsKeyDown(Key.OemTilde))
            {
                this.ContextMenu = buildContextMenu();
                this.ContextMenu.IsOpen = true;
            }
        }
        
        private string hostedAppName()
        {
            return (string)config["hosted_app_window"]["name"];
        }

        private ContextMenu buildContextMenu()
        {
            log("build custom menu");

            ContextMenu menu = new ContextMenu();

            MenuItem start = new MenuItem();
            start.Header = "Start " + hostedAppName();
            start.IsEnabled = dockedWindowAndSubProcess.subProcess == null;
            start.Click += (innerSender, args) => startAndDockHostedApp();
            menu.Items.Add(start);

            MenuItem stop = new MenuItem();
            stop.Header = "Stop " + hostedAppName();
            stop.IsEnabled = dockedWindowAndSubProcess.subProcess != null;
            stop.Click += (innerSender, args) => stopHostedApp();
            menu.Items.Add(stop);

            MenuItem restart = new MenuItem();
            restart.Header = "Restart " + hostedAppName();
            restart.IsEnabled = dockedWindowAndSubProcess.subProcess != null;
            restart.Click += (innerSender, args) => { if (stopHostedApp()) startAndDockHostedApp(); };
            menu.Items.Add(restart);

            MenuItem browseToUrl = new MenuItem();
            browseToUrl.Header = "Browse To URL...";
            browseToUrl.Click += (innerSender, args) => {
                string currentUrl = Browser.WebBrowser.Address.ToString();
                string newUrl = Interaction.InputBox("Browse To URL...", "URL", currentUrl, 0, 0);
                loadUrlInBrowser(newUrl);
                updateWindowTitle();
            };
            menu.Items.Add(browseToUrl);

            return menu;
        }
        
        private void startAndDockHostedApp()
        {
            Contract.Requires(config != null, "config not loaded");

            if (dockedWindowAndSubProcess.subProcess != null)
            {
                MessageBox.Show(hostedAppName() + " is already running.", "PID=" + dockedWindowAndSubProcess.subProcess.Id);
            }

            ProcessStartInfo processStartInfo = null;

            if (config["hosted_app_window"]["process_info"]["java_executable_path"] != null)
            {
                // Minecraft arguments:
                // https://github.com/tomsik68/mclauncher-api/wiki/Minecraft-1.6-Launcher

                processStartInfo = UIProcessUtil.assembleJavaProcessStartInfo(
                    (string)config["hosted_app_window"]["process_info"]["java_executable_path"],
                    config["hosted_app_window"]["process_info"]["java_x_options"].Select(j => j.ToString()).ToArray(),
                    config["hosted_app_window"]["process_info"]["java_system_properties"].Select(j => j.ToString()).ToArray(),
                    config["hosted_app_window"]["process_info"]["java_classpath_components"].Select(j => j.ToString()).ToArray(),
                    (string)config["hosted_app_window"]["process_info"]["java_main_class"],
                    config["hosted_app_window"]["process_info"]["java_program_arguments"].Select(j => j.ToString()).ToArray());
            } else
            {
                processStartInfo = new ProcessStartInfo((string)config["hosted_app_window"]["process_info"]["file_name"]);
                processStartInfo.Arguments = (string)config["hosted_app_window"]["process_info"]["arguments"];
            }

            processStartInfo.WindowStyle = ProcessWindowStyle.Maximized;

            dockedWindowAndSubProcess = UIProcessUtil.DockSubProcessWindow(
                this,
                processStartInfo,
                (string)config["hosted_app_window"]["wait_for_window_title_starts_with"],
                HostedAppWindow);
            
            dockedWindowAndSubProcess.subProcess.BeginOutputReadLine();
            dockedWindowAndSubProcess.subProcess.BeginErrorReadLine();
            dockedWindowAndSubProcess.subProcess.OutputDataReceived += (innerSender, args) => log("STDOUT [" + dockedWindowAndSubProcess.subProcess.Id + "] " + args.Data);
            dockedWindowAndSubProcess.subProcess.ErrorDataReceived += (innerSender, args) => log("STDERR [" + dockedWindowAndSubProcess.subProcess.Id + "] " + args.Data);

            HostedAppWindow_Resize(new Object(), new EventArgs());
        }

        private void focusOnHostedAppWindow()
        {
            log("focus on hosted app");
            UIProcessUtil.focusOnWindowWithHandle(dockedWindowAndSubProcess.dockedWindowHandle);
            HostedAppWindow.BorderBrush = new SolidColorBrush(Colors.Magenta);
            browserBorder.BorderBrush = new SolidColorBrush(Colors.Gray);
        }

        private void focusOnBrowserWindow()
        {
            log("focus on browser");
            UIProcessUtil.focusOnWindowWithHandle(new WindowInteropHelper(this).Handle);
            Browser.Focus();
            Keyboard.Focus(Browser);
            HostedAppWindow.BorderBrush = new SolidColorBrush(Colors.Gray);
            browserBorder.BorderBrush = new SolidColorBrush(Colors.Magenta);
        }

        private void loadUrlInBrowser(string url)
        {
            log("Browser load url " + url);
            Browser.Load(url);
        }

        private void toggleFocus()
        {
            if (dockedWindowAndSubProcess.dockedWindowHandle != IntPtr.Zero)
            {
                
                if (focusToggle)
                {
                    focusOnHostedAppWindow();
                }
                else
                {
                    focusOnBrowserWindow();
                }
                focusToggle = !focusToggle;
            }
            else
            {
                log("not changing focus because there's no docked window.");
            }
        }

        private bool stopHostedApp()
        {
            if (dockedWindowAndSubProcess.subProcess == null)
            {
                MessageBox.Show("Can't stop " + hostedAppName() + " because it isn't running.");
                return false;
            }
            else
            {
                killHostedApp();
                return true;
            }
        }

        private void killHostedApp()
        {
            if (dockedWindowAndSubProcess.subProcess != null && 
                !dockedWindowAndSubProcess.subProcess.HasExited)
            {
                log("killing hosted app");
                dockedWindowAndSubProcess.subProcess.Kill();
                dockedWindowAndSubProcess.subProcess.WaitForExit();
                dockedWindowAndSubProcess.subProcess = null;
                dockedWindowAndSubProcess.dockedWindowHandle = IntPtr.Zero;
            }
        }

        private void shutdown()
        {
            killHostedApp();
            f12ToggleKeyHook.stopListeningForKeyPress();
        }

        void log(string output)
        {
            syncContext.Post(_ => Trace.TraceInformation(output), null);
        }
        
        private string nativeDllExtractDir()
        {
            return (string)config["hosted_app_window"]["process_info"]["java_system_properties"]
                .Single(s => s.ToString().StartsWith("-Djava.library.path="))
                .ToString().Replace("-Djava.library.path=", "");
        }

        private void extractNativeJars()
        {
            if (config["hosted_app_window"]["process_info"]["native_jars"] == null)
            {
                return;
            }
            ZipJarUtil.unzipArchivesToDir(
                config["hosted_app_window"]["process_info"]["native_jars"].Select(j => j.ToString()).ToArray(),
                nativeDllExtractDir());
        }
    }
}
