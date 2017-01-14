using System;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Threading;
using System.Net.Http;
using System.Net.Http.Headers;

namespace mcprog2.Util
{
    class LogToServerUtil
    {
        public static void postLogLinesToServerRegularly(
            InMemoryTraceListener logLinesHolder, 
            Uri loggingUri, 
            string basicAuthUsername, 
            string basicAuthPassword, 
            int sleepMsBetweenLogPostAttempts,
            int sleepMsBetweenRetriesAfterPostFailure, 
            int maxRetries)
        {
            while (true)
            {
                try
                {
                    string[] logLines = logLinesHolder.dequeueAll();

                    if (logLines.Length == 0)
                    {
                        // note: this will have the effect of adding to log lines held by
                        // the InMemoryTraceListener, in effect creating a heartbeat, which is 
                        // intentional. 
                        Trace.TraceInformation("Server log post: no log lines found, sleeping.");
                    }
                    else
                    {
                        string logLinesJoined = string.Join("", logLines);
                        bool success = httpPostUntilSuccess(
                            logLinesJoined,
                            loggingUri,
                            basicAuthUsername,
                            basicAuthPassword,
                            sleepMsBetweenRetriesAfterPostFailure,
                            maxRetries);
                        if (success)
                        {
                            // intentionally written to the console
                            // (this would cause too much noise in the server log 
                            // and is unimportant except for debugging in development)
                            Console.WriteLine("posted " + logLines.Length + " log lines to '" + loggingUri.ToString() + "'");
                        }
                    }

                    Thread.Sleep(sleepMsBetweenLogPostAttempts);
                }
                catch (Exception ex)
                {
                    Trace.TraceError(ex.ToString());
                }
            }
        }

        private static bool httpPostUntilSuccess(string requestBody, Uri uri, string basicAuthUsername, string basicAuthPassword, int sleepMsBetweenRetries, int maxRetries)
        {
            int i = 0;
            bool success = false;
            do
            {
                success = httpPost(requestBody, uri, basicAuthUsername, basicAuthPassword);
                i++;
                if (!success)
                {
                    Trace.TraceError("detected failure in http post to '', will retry in " +
                        sleepMsBetweenRetries + " ms. Tries so far: " + i + ", try limit: " + maxRetries + ".");
                    Thread.Sleep(sleepMsBetweenRetries);
                }
            } while (!success && i < maxRetries);

            return success;
        }

        private static bool httpPost(string requestBody, Uri uri, string basicAuthUsername, string basicAuthPassword)
        {
            HttpClient client = new HttpClient();
            var credentials = Convert.ToBase64String(Encoding.ASCII.GetBytes(string.Format("{0}:{1}", basicAuthUsername, basicAuthPassword)));
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", credentials);
            HttpRequestMessage request = new HttpRequestMessage();
            request.Method = HttpMethod.Post;
            request.RequestUri = uri;

            ASCIIEncoding encoding = new ASCIIEncoding();
            byte[] requestBodyBytes = encoding.GetBytes(requestBody);
            request.Content = new ByteArrayContent(requestBodyBytes);

            Task<HttpResponseMessage> responseTask = client.SendAsync(request);
            responseTask.Wait();
            HttpResponseMessage response = responseTask.Result;

            bool isOk = response.StatusCode == System.Net.HttpStatusCode.OK;

            if (!isOk)
            {
                Trace.TraceError("http error when posting to '" + uri.ToString() + "': " + response.ToString());
            }

            return isOk;
        }
    }
}
