using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using Newtonsoft.Json.Schema;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Diagnostics.Contracts;
using System.Diagnostics;

namespace mcprog2.Util
{
    class GlobalSettings
    {
        private static Dictionary<string, string> settings = new Dictionary<string, string>();

        private static void addSetting(string key, string value)
        {
            Contract.Requires(!settings.ContainsKey(key), "will not override setting. key='" + key +
                "' newValue='" + value + "'");
            Trace.TraceInformation("add global setting: key='" + key + "' value='" + value + "'");

            settings[key] = value;
        }

        public static void loadFromSystemEnvironment()
        {
            addSetting("appdata", Environment.GetEnvironmentVariable("APPDATA"));
            addSetting("program_files_x86", Environment.GetEnvironmentVariable("PROGRAMFILES(X86)"));
        }

        public static void loadFromJsonConfig(JObject config)
        {
            loadStaticVariables(config);
            loadMinecraftProfileVariables(config);
        }

        private static void loadStaticVariables(JObject config)
        {
            if (config["hosted_app_window"]["variables"] !=null && 
                config["hosted_app_window"]["variables"]["static"] != null)
            {
                foreach (JProperty p in config["hosted_app_window"]["variables"]["static"])
                {
                    addSetting(p.Name, p.Value.ToString());
                }
            }
        }

        private static void loadMinecraftProfileVariables(JObject config)
        {
            if (MinecraftUtil.hasMinecraftLauncherProfilesJson(config))
            {
                Dictionary<string, string> profileContents = MinecraftUtil.loadSelectedMinecraftProfileFromLauncherProfilesJson(config);
                
                foreach (KeyValuePair<string, string> kv in profileContents)
                {
                    addSetting("selected_minecraft_launcher_profile:" + kv.Key, kv.Value);
                }
            }
        }

        public static string substitute(string input)
        {
            foreach (string k in settings.Keys)
            {
                string searchFor = "%" + k + "%";
                if (input.Contains(searchFor))
                {
                    Trace.TraceInformation("variable replacement: found key '" + searchFor + "', replacing with value '" + settings[k] + "' full original string: '" + input + "'");
                    input = input.Replace(searchFor, settings[k]);
                }
            }

            return input;
        }
    }
}
