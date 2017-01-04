using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Interop;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.Windows.Forms;
using System.Diagnostics.Contracts;

namespace mcprog2.Util
{
    // see https://blogs.msdn.microsoft.com/toub/2006/05/03/low-level-keyboard-hook-in-c/

    class GlobalKeyHook
    {
        private const int WH_KEYBOARD_LL = 13;
        private const int WM_KEYDOWN = 0x0100;

        private LowLevelKeyboardProc proc;
        private IntPtr hookId = IntPtr.Zero;
        private int listenForKeyCode;
        private Action onKeyPressed;

        public GlobalKeyHook(Keys listenForKeyCode, Action onKeyPressed)
        {
            this.listenForKeyCode = (int)listenForKeyCode;
            this.onKeyPressed = onKeyPressed;
            this.proc = HookCallback;
        }

        public void startListeningForKeyPress()
        {
            Trace.TraceInformation("GlobalKeyHook: start listening for key press, keycode=" + this.listenForKeyCode);
            hookId = SetHook(proc);
        }

        public void stopListeningForKeyPress()
        {
            Trace.TraceInformation("GlobalKeyHook: stop listening for key press, keycode=" + this.listenForKeyCode);
            Contract.Requires(hookId != IntPtr.Zero);
            UnhookWindowsHookEx(hookId);
            hookId = IntPtr.Zero;
        }

        private IntPtr SetHook(LowLevelKeyboardProc proc)
        {
            using (Process curProcess = Process.GetCurrentProcess())
            using (ProcessModule curModule = curProcess.MainModule)
            {
                return SetWindowsHookEx(WH_KEYBOARD_LL, proc,
                    GetModuleHandle(curModule.ModuleName), 0);
            }
        }

        private delegate IntPtr LowLevelKeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);

        private IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
        {
            if (nCode >= 0 && wParam == (IntPtr)WM_KEYDOWN)
            {
                int vkCode = Marshal.ReadInt32(lParam);
                if (vkCode == listenForKeyCode)
                {
                    Debug.Print("key " + listenForKeyCode + " detected");
                    onKeyPressed();
                }
            }
            return CallNextHookEx(hookId, nCode, wParam, lParam);
        }

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr SetWindowsHookEx(int idHook, LowLevelKeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool UnhookWindowsHookEx(IntPtr hhk);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr GetModuleHandle(string lpModuleName);
    }
}
