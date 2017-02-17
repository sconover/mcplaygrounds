using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Schema;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using System.Net;

namespace mcprog2.Util
{
    class ConfigUtil
    {
        public static string getLatestBrowserUrlFromConfig()
        {
            return (string)load().serverConfig["browser_window"]["url"];
        }

        public static AllConfig load()
        {
            BootstrapConfig bootstrap = loadBootstrapConfig();

            JObject serverConfig = 
                loadConfig(
                    bootstrap.ConfigUri,
                    bootstrap.BasicAuthUsername,
                    bootstrap.BasicAuthPassword);

            AllConfig allConfig = new AllConfig();
            allConfig.bootstrapConfig = bootstrap;
            allConfig.serverConfig = serverConfig;
            return allConfig;
        }

        public static BrowserBasicAuthPopulator loadBasicAuthPopulatorFromBootstrapJson()
        {
            BootstrapConfig bootstrap = loadBootstrapConfig();
            return new BrowserBasicAuthPopulator(bootstrap.ConfigUri.Host, bootstrap.BasicAuthUsername, bootstrap.BasicAuthPassword);
        }

        public struct AllConfig
        {
            public BootstrapConfig bootstrapConfig;
            public JObject serverConfig;
        }

        private static JObject loadConfig(Uri uri, string username, string password)
        {
            Trace.TraceInformation("Config: loading from '" + uri.ToString() + "' with username '" + username + "'");
            WebClient client = new WebClient { Credentials = new NetworkCredential(username, password) };
            string json = client.DownloadString(uri);
            JObject config = JObject.Parse(json);
            IList<string> messages;
            bool valid = config.IsValid(loadConfigJsonSchema(), out messages);
            if (!valid)
            {
                throw new Exception("JSON Schema validation: " + string.Join(", ", messages));
            }
            return config;
        }
        
        private static JsonSchema loadConfigJsonSchema()
        {
            string content = File.ReadAllText(filePathRelativeToProcess("native-client-config-schema.json"));
            return JsonSchema.Parse(content);
        }

        private static string filePathRelativeToProcess(string relativePath)
        {
            string path = Path.GetDirectoryName(Process.GetCurrentProcess().MainModule.FileName) + "\\" + relativePath;
            Contract.Requires(File.Exists(path), "file not found: " + path);
            return path;
        }

        public struct BootstrapConfig
        {
            public Uri ConfigUri;
            public Uri AppendLogUri;
            public string BasicAuthUsername;
            public string BasicAuthPassword;
        }

        private static BootstrapConfig loadBootstrapConfig()
        {
            string bootstrapFilePath = filePathRelativeToProcess("bootstrap.json");
            JObject bootstrap = JObject.Parse(File.ReadAllText(bootstrapFilePath));
            if (bootstrap["base_uri"] == null ||
                bootstrap["config_path"] == null ||
                bootstrap["basic_auth_username"] == null ||
                bootstrap["basic_auth_password"] == null)
            {
                throw new Exception("invalid bootstrap.json");
            }

            Uri configUri = null;
            string configUriStr = (string)bootstrap["base_uri"] + (string)bootstrap["config_path"];
            if (configUriStr.StartsWith("http://example.com") || !configUriStr.StartsWith("file") && !configUriStr.StartsWith("http"))
            {
                configUri = uriFromRelativeFilePathToProcess((string)bootstrap["config_path"]);
            }
            else
            {
                configUri = new Uri(configUriStr);
            }

            // NOTE: there MUST be agreement between this path, and the 
            // append log endpoint defined in server code/config.
            Uri appendLogUri = new Uri((string)bootstrap["base_uri"] + "/appendlog");

            BootstrapConfig b = new BootstrapConfig();
            b.AppendLogUri = appendLogUri;
            b.ConfigUri = configUri;
            b.BasicAuthUsername = (string)bootstrap["basic_auth_username"];
            b.BasicAuthPassword = (string)bootstrap["basic_auth_password"];
            return b;
        }

        private static Uri uriFromRelativeFilePathToProcess(string relativePath)
        {
            return new System.Uri(filePathRelativeToProcess(relativePath));
        }
    }
}
