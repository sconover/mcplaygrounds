using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CefSharp;
using System.Diagnostics;

namespace mcprog2.Util
{
    class BrowserBasicAuthPopulator : IRequestHandler
    {
        private string targetHost;
        private string basicAuthUsername;
        private string basicAuthPassword;

        public BrowserBasicAuthPopulator(string targetHost, string basicAuthUsername, string basicAuthPassword)
        {
            this.targetHost = targetHost;
            this.basicAuthUsername = basicAuthUsername;
            this.basicAuthPassword = basicAuthPassword;
        }

        public bool GetAuthCredentials(IWebBrowser browserControl, IBrowser browser, IFrame frame, bool isProxy, string host, int port, string realm, string scheme, IAuthCallback callback)
        {
            // "Return true to continue the request and call CefAuthCallback::Continue() when the 
            // authentication information is available. Return false to cancel the request."
            
            if (host == targetHost)
            {
                Trace.TraceInformation("because host is '" + host + "', providing basic auth creds, username='" + basicAuthUsername + "'");
                callback.Continue(basicAuthUsername, basicAuthPassword);
            }
            return true;
        }


        // the rest of these methods return values that cause the default browser behavior to occur

        public IResponseFilter GetResourceResponseFilter(IWebBrowser browserControl, IBrowser browser, IFrame frame, IRequest request, IResponse response)
        {
            // "Return an IResponseFilter to intercept this response, otherwise return null"
            return null; 
        }

        public bool OnBeforeBrowse(IWebBrowser browserControl, IBrowser browser, IFrame frame, IRequest request, bool isRedirect)
        {
            // "Return true to cancel the navigation or false to allow the navigation to proceed."
            return false; 
        }

        public CefReturnValue OnBeforeResourceLoad(IWebBrowser browserControl, IBrowser browser, IFrame frame, IRequest request, IRequestCallback callback)
        {
            // "To cancel loading of the resource return Cancel or Continue to allow the resource 
            // to load normally. For async return ContinueAsync"
            return CefReturnValue.Continue; 
        }

        public bool OnCertificateError(IWebBrowser browserControl, IBrowser browser, CefErrorCode errorCode, string requestUrl, ISslInfo sslInfo, IRequestCallback callback)
        {
            // "Return false to cancel the request immediately. Return true and use IRequestCallback to execute in an async fashion."
            return true;
        }

        public bool OnOpenUrlFromTab(IWebBrowser browserControl, IBrowser browser, IFrame frame, string targetUrl, WindowOpenDisposition targetDisposition, bool userGesture)
        {
            // "Return true to cancel the navigation or false to allow the navigation to proceed in the source browser's top-level frame."
            return false;
        }

        public void OnPluginCrashed(IWebBrowser browserControl, IBrowser browser, string pluginPath)
        {
            // do nothing
        }

        public bool OnProtocolExecution(IWebBrowser browserControl, IBrowser browser, string url)
        {
            // "return to true to attempt execution via the registered OS protocol handler, if any. Otherwise return false."
            return true;
        }

        public bool OnQuotaRequest(IWebBrowser browserControl, IBrowser browser, string originUrl, long newSize, IRequestCallback callback)
        {
            // "Return false to cancel the request immediately. Return true to continue the request and call
            // Continue(Boolean) either in this method or at a later time to grant or deny the request."
            return true;
        }

        public void OnRenderProcessTerminated(IWebBrowser browserControl, IBrowser browser, CefTerminationStatus status)
        {
            // do nothing
        }

        public void OnRenderViewReady(IWebBrowser browserControl, IBrowser browser)
        {
            // do nothing
        }

        public void OnResourceLoadComplete(IWebBrowser browserControl, IBrowser browser, IFrame frame, IRequest request, IResponse response, UrlRequestStatus status, long receivedContentLength)
        {
            // do nothing
        }

        public void OnResourceRedirect(IWebBrowser browserControl, IBrowser browser, IFrame frame, IRequest request, ref string newUrl)
        {
            // do nothing
        }

        public bool OnResourceResponse(IWebBrowser browserControl, IBrowser browser, IFrame frame, IRequest request, IResponse response)
        {
            // "To allow the resource to load normally return false. To redirect or retry the resource modify 
            // request (url, headers or post body) and return true."
            return false;
        }
    }
}
