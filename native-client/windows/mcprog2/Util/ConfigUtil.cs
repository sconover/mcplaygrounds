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
        private static JObject loadConfig(Uri uri, string username, string password)
        {
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
            string content = File.ReadAllText(filePathRelativeToProcess("config-schema.json"));
            return JsonSchema.Parse(content);
        }

        private static string filePathRelativeToProcess(string relativePath)
        {
            string path = Path.GetDirectoryName(Process.GetCurrentProcess().MainModule.FileName) + "\\" + relativePath;
            Contract.Requires(File.Exists(path), "file not found: " + path);
            return path;
        }

        public static JObject load()
        {
            BootstrapConfig bootstrap = loadBootstrapConfig();
         
            return loadConfig(
                bootstrap.ConfigUri, 
                bootstrap.BasicAuthUsername, 
                bootstrap.BasicAuthPassword);
        }

        public static BasicAuthPopulator loadBasicAuthPopulatorFromBootstrapJson()
        {
            BootstrapConfig bootstrap = loadBootstrapConfig();
            return new BasicAuthPopulator(bootstrap.ConfigUri.Host, bootstrap.BasicAuthUsername, bootstrap.BasicAuthPassword);
        }

        private struct BootstrapConfig
        {
            public Uri ConfigUri;
            public string BasicAuthUsername;
            public string BasicAuthPassword;
        }

        private static BootstrapConfig loadBootstrapConfig()
        {
            string bootstrapFilePath = filePathRelativeToProcess("bootstrap.json");
            JObject bootstrap = JObject.Parse(File.ReadAllText(bootstrapFilePath));
            if (bootstrap["uri"] == null ||
                bootstrap["basic_auth_username"] == null ||
                bootstrap["basic_auth_password"] == null)
            {
                throw new Exception("invalid bootstrap.json");
            }

            Uri uri = null;
            string uriStr = (string)bootstrap["uri"];
            if (!uriStr.StartsWith("file") && !uriStr.StartsWith("http"))
            {
                uri = uriFromRelativeFilePathToProcess(uriStr);
            }
            else
            {
                uri = new Uri(uriStr);
            }

            BootstrapConfig b = new BootstrapConfig();
            b.ConfigUri = uri;
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
