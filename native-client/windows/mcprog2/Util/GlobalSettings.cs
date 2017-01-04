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
            if (config["hosted_app_window"]["variables"] != null &&
                config["hosted_app_window"]["variables"]["load_selected_minecraft_profile_from_launcher_profiles_json"] != null)
            {
                string path = substitute((string)config["hosted_app_window"]["variables"]["load_selected_minecraft_profile_from_launcher_profiles_json"]);
                Dictionary<string, string> profileContents = getSelectedMinecraftProfileFromLauncherProfilesJson(path);
                
                foreach (KeyValuePair<string, string> kv in profileContents)
                {
                    addSetting("selected_minecraft_launcher_profile:" + kv.Key, kv.Value);
                }
            }
        }

        private static Dictionary<string, string> getSelectedMinecraftProfileFromLauncherProfilesJson(string launcherProfilesJsonPath)
        {
            Contract.Requires(File.Exists(launcherProfilesJsonPath), "file not found: " + launcherProfilesJsonPath);
            JObject lp = JObject.Parse(File.ReadAllText(launcherProfilesJsonPath));
            
            if (lp["selectedUser"] != null &&
                lp["authenticationDatabase"] != null &&
                lp["authenticationDatabase"][lp["selectedUser"].ToString()] != null)
            {
                Dictionary<string, string> result = new Dictionary<string, string>();
                foreach (JProperty p in lp["authenticationDatabase"][lp["selectedUser"].ToString()])
                {
                    result[p.Name] = p.Value.ToString();
                }
                return result;
            }
            else
            {
                return new Dictionary<string, string>();
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
