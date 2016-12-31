using System.Diagnostics;
using System;
using System.Linq;
using mcprog2.Util;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows.Interop;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Threading;

namespace mcprog2.Util
{
    // http://stackoverflow.com/a/5965992
    // http://stackoverflow.com/a/6484591

    class UIProcessUtil
    {
        public static ProcessStartInfo assembleJavaProcessStartInfo(
            string javaExecutablePath,
            string[] javaXOptions,
            string[] javaSystemProperties,
            string[] javaClasspathComponents,
            string javaMainClass,
            string[] javaProgramArguments)
        {
            string executable = doubleQuote(GlobalSettings.substitute(javaExecutablePath));

            string argumentStr = "";
            argumentStr += string.Join(" ", javaXOptions.Select(str => doubleQuote(GlobalSettings.substitute(str))));
            argumentStr += " ";
            argumentStr += string.Join(" ", javaSystemProperties.Select(str => doubleQuote(GlobalSettings.substitute(str))));
            argumentStr += " -cp ";
            argumentStr += doubleQuote(string.Join(";", javaClasspathComponents.Select(str => GlobalSettings.substitute(str))));
            argumentStr += " ";
            argumentStr += GlobalSettings.substitute(javaMainClass);
            argumentStr += " ";
            argumentStr += string.Join(" ", javaProgramArguments.Select(str => GlobalSettings.substitute(str)));
            Console.WriteLine("returning assembled java command: executable: " + executable + " argumentStr: " + argumentStr);

            ProcessStartInfo processStartInfo = new ProcessStartInfo(executable);
            processStartInfo.Arguments = argumentStr;
            return processStartInfo;
        }

        private static string doubleQuote(string input)
        {
            return "\"" + input + "\"";
        }

        private static void logProcessStartInfo(ProcessStartInfo p)
        {
            Console.WriteLine("PROCESSINFO filename='" + p.FileName + "' arguments='" + p.Arguments + "'");
        }

        private static string toDebugString(Process p, String comment)
        {
            p.Refresh();
            return "PROCESS['" + comment + "'] id=" + p.Id +
                " name=" + p.ProcessName +
                " session=" + p.SessionId +
                " mainwindowtitle=" + p.MainWindowTitle +
                " handle=" + p.MainWindowHandle +
                " tostring=" + p.ToString();
        }

        private static void logProcess(Process p, String comment)
        {
            Console.WriteLine(toDebugString(p, comment));
        }

        private static IntPtr waitForWindowHavingTitleStartingWith(Process process, String windowTitleStartsWith)
        {
            Console.WriteLine("waiting for window to appear, having title starting with '" + windowTitleStartsWith +
                "', and created by process: " + toDebugString(process, "waitForWindow"));
            while (true)
            {
                process.Refresh();
                if (process.HasExited)
                {
                    logProcess(process, "process exited, stopping search for window.");
                    return IntPtr.Zero;
                }

                List<IntPtr> handles = enumerateProcessWindowHandles(process.Id);
                foreach (IntPtr handle in enumerateProcessWindowHandles(process.Id))
                {
                    if (getWindowTitle(handle).StartsWith(windowTitleStartsWith))
                    {
                        logWindowFromHandle(handle, "found-window-with-title['" + windowTitleStartsWith + "']");
                        return handle;
                    }
                }
                Thread.Sleep(50);
            }
        }

        private delegate bool EnumThreadDelegate(IntPtr hWnd, IntPtr lParam);

        [DllImport("user32.dll")]
        private static extern bool EnumThreadWindows(int dwThreadId, EnumThreadDelegate lpfn, IntPtr lParam);

        private static List<IntPtr> enumerateProcessWindowHandles(int processId)
        {
            var handles = new List<IntPtr>();

            foreach (ProcessThread thread in Process.GetProcessById(processId).Threads)
                EnumThreadWindows(thread.Id,
                    (hWnd, lParam) => { handles.Add(hWnd); return true; }, IntPtr.Zero);

            return handles;
        }

        private static void logFrameworkElement(FrameworkElement element, string comment)
        {
            Console.WriteLine("Border['" + comment + "']" +
                " actualwidth=" + element.ActualWidth +
                " actualheight=" + element.ActualHeight);
        }

        private static void logWindowFromHandle(IntPtr handle, string comment)
        {
            Console.WriteLine("Window['" + comment +
                "' handle=" + handle.ToString() +
                " title='" + getWindowTitle(handle) +
                "']");
        }

        [DllImport("user32.dll")]
        private static extern int GetWindowTextLength(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

        private static string getWindowTitle(IntPtr windowHandle)
        {
            int length = GetWindowTextLength(windowHandle);
            StringBuilder text = new StringBuilder(length + 1);
            GetWindowText(windowHandle, text, text.Capacity);
            return text.ToString();
        }


        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool GetWindowRect(HandleRef hWnd, out RECT lpRect);

        [StructLayout(LayoutKind.Sequential)]
        private struct RECT
        {
            public int Left;        // x position of upper-left corner
            public int Top;         // y position of upper-left corner
            public int Right;       // x position of lower-right corner
            public int Bottom;      // y position of lower-right corner
        }

        private static void logWindowRectFromHandle(object wrapper, IntPtr handle, string comment)
        {
            RECT rct;
            GetWindowRect(new HandleRef(wrapper, handle), out rct);

            Console.WriteLine("Window['" + comment +
                "' handle=" + handle.ToString() +
                " title='" + getWindowTitle(handle) +
                "'] rect: " +
                " left=" + rct.Left +
                " top=" + rct.Top +
                " right=" + rct.Right +
                " bottom=" + rct.Bottom +
                " width=" + (rct.Right - rct.Left) +
                " height=" + (rct.Bottom - rct.Top));
        }

        [DllImport("user32.dll")]
        private static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

        public struct DockedWindowAndSubProcess
        {
            public Process subProcess;
            public IntPtr dockedWindowHandle;
        }

        public static DockedWindowAndSubProcess DockSubProcessWindow(
            Window hostWindow,
            ProcessStartInfo subProcessStartInfo,
            String waitForWindowWithTitleStartingWith,
            FrameworkElement dockIntoElement)
        {
            DockedWindowAndSubProcess result;

            IntPtr hostWindowHandle = new WindowInteropHelper(hostWindow).Handle;
            logWindowRectFromHandle(hostWindow, hostWindowHandle, "host");

            subProcessStartInfo.UseShellExecute = false;
            subProcessStartInfo.CreateNoWindow = true;
            subProcessStartInfo.RedirectStandardOutput = true;
            subProcessStartInfo.RedirectStandardError = true;

            logProcessStartInfo(subProcessStartInfo);
            Process subProcess = Process.Start(subProcessStartInfo);
            logProcess(subProcess, "dockSubProcessWindow-start-subProcess");

            IntPtr dockedWindowHandle = waitForWindowHavingTitleStartingWith(subProcess, waitForWindowWithTitleStartingWith);
            logWindowRectFromHandle(hostWindow, dockedWindowHandle, "docked");

            Console.WriteLine("SetParent of window=" + dockedWindowHandle + " to window=" + hostWindowHandle);
            //returns the handle of the window's parent prior to this call.
            IntPtr originalWindowParentHandle = SetParent(dockedWindowHandle, hostWindowHandle);
            logWindowRectFromHandle(hostWindow, originalWindowParentHandle, "original-parent");

            simplifyWindow(dockedWindowHandle);

            result.subProcess = subProcess;
            result.dockedWindowHandle = dockedWindowHandle;
            return result;
        }


        // see http://stackoverflow.com/questions/2825528/removing-the-title-bar-of-external-application-using-c-sharp
        // see http://stackoverflow.com/questions/2832217/modify-the-windows-style-of-another-application-using-winapi

        //Sets window attributes
        [DllImport("USER32.DLL")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool ShowScrollBar(IntPtr hWnd, int wBar, bool bShow);

        //assorted constants needed
        private static int GWL_STYLE = -16;
        private static uint WS_OVERLAPPED = 0x80000000;

        private static void simplifyWindow(IntPtr windowHandle)
        {
            // "overlapped" will be the basic kind of window
            SetWindowLong(windowHandle, GWL_STYLE, WS_OVERLAPPED);
        }

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);

        public static void MakeWindowSameSizeAndPositionAsElement(object wrapper, IntPtr dockedWindowHandle, FrameworkElement matchingElement, int margin)
        {
            logWindowRectFromHandle(wrapper, dockedWindowHandle, "RESIZE-docked-before-resize");

            //Change the docked windows size to match its parent's size. 
            //For some reason, multiplying the H and W by 1.5 seems to actually fill the window.
            //TODO: make this configurable in case it's wrong
            logFrameworkElement(matchingElement, "RESIZE-containing-border-before-resize");
            MoveWindow(dockedWindowHandle, margin, margin, (int)(matchingElement.ActualWidth * 1.5 - margin * 1.5), (int)(matchingElement.ActualHeight * 1.5 - margin * 1.5), true);
            logWindowRectFromHandle(wrapper, dockedWindowHandle, "RESIZE-docked-after-resize");
        }


        [DllImport("user32.dll")]
        private static extern IntPtr GetActiveWindow();

        [DllImport("user32.dll")]
        private static extern IntPtr GetFocus();

        public static bool doesWindowWithHandleHaveFocus(IntPtr windowHandle)
        {
            return GetActiveWindow() == windowHandle;
        }


        // It's pretty incredible that it takes the following to cause 
        // a given window to appear in the foreground consistently, but the following really
        // got the job done where simpler solutions were very inconsistent. 
        // https://shlomio.wordpress.com/2012/09/04/solved-setforegroundwindow-win32-api-not-always-works/

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

        // When you don't want the ProcessId, use this overload and pass 
        // IntPtr.Zero for the second parameter
        [DllImport("user32.dll")]
        private static extern uint GetWindowThreadProcessId(IntPtr hWnd,
            IntPtr ProcessId);

        [DllImport("kernel32.dll")]
        private static extern uint GetCurrentThreadId();

        /// The GetForegroundWindow function returns a handle to the 
        /// foreground window.
        [DllImport("user32.dll")]
        private static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        private static extern bool AttachThreadInput(uint idAttach,
            uint idAttachTo, bool fAttach);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool BringWindowToTop(IntPtr hWnd);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool BringWindowToTop(HandleRef hWnd);

        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, uint nCmdShow);

        private static void attachedThreadInputAction(Action action)
        {
            var foreThread = GetWindowThreadProcessId(GetForegroundWindow(), IntPtr.Zero);
            var appThread = GetCurrentThreadId();
            bool threadsAttached = false;

            try
            {
                threadsAttached =
                    foreThread == appThread ||
                    AttachThreadInput(foreThread, appThread, true);

                if (threadsAttached) action();
                else throw new ThreadStateException("AttachThreadInput failed.");
            }
            finally
            {
                if (threadsAttached)
                    AttachThreadInput(foreThread, appThread, false);
            }
        }

        private const uint SW_SHOW = 5;
        
        public static IntPtr focusOnWindowWithHandle(IntPtr hwnd)
        {
            attachedThreadInputAction(
                () =>
                {
                    BringWindowToTop(hwnd);
                    ShowWindow(hwnd, SW_SHOW);
                });

            return GetFocus();
        }
    }
}