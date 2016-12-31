using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CefSharp;

namespace mcprog2.Util
{
    class BrowserLifeSpanHandler : ILifeSpanHandler
    {
        // change the default brower behavior to load urls "popped up" in new windows,
        // in the current frame instead.

        public bool OnBeforePopup(IWebBrowser browserControl, IBrowser browser, IFrame frame, string targetUrl, string targetFrameName, WindowOpenDisposition targetDisposition, bool userGesture, IPopupFeatures popupFeatures, IWindowInfo windowInfo, IBrowserSettings browserSettings, ref bool noJavascriptAccess, out IWebBrowser newBrowser)
        {
            // "To cancel creation of the popup window return true."

            browserControl.Load(targetUrl);
            newBrowser = browserControl;
            return true;
        }


        // the rest of these methods are intended to not change default browser behavior

        public bool DoClose(IWebBrowser browserControl, IBrowser browser)
        {
            // "For default behaviour return false"
            return false;
        }

        public void OnAfterCreated(IWebBrowser browserControl, IBrowser browser)
        {
            // do nothing
        }

        public void OnBeforeClose(IWebBrowser browserControl, IBrowser browser)
        {
            // do nothing
        }
    }
}
