using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static mcprog2.Util.ConfigUtil;
using Newtonsoft.Json.Schema;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Diagnostics.Contracts;

namespace mcprog2.Util
{
    class MinecraftUtil
    {
        // launcher profile sample:
        //
        //{
        //  "profiles": {
        //    "de311e853e5f2e2ae0e22234da4d8264": {
        //      "type": "latest-release",
        //      "lastUsed": "1970-01-01T00:00:00.001Z"
        //    },
        //    "55ad96fc4182651ad8510826214760eb": {
        //      "type": "latest-snapshot",
        //      "lastUsed": "1970-01-01T00:00:00.000Z"
        //    },
        //    "papa": {
        //      "name": "papa",
        //      "type": "custom",
        //      "created": "1970-01-01T00:00:00.002Z",
        //      "lastUsed": "2017-02-10T17:31:18.980Z",
        //      "lastVersionId": "1.8.9"
        //    }
        //  },
        //  "clientToken": "867dc236-40ac-4b62-8317-bd3876951883",
        //  "authenticationDatabase": {
        //    "27ba064ffe9e988e96812adb47437237": {
        //      "accessToken": "22ad2ffed73b4d8c8c88ec921b1004de",
        //      "username": "bar@gmail.com",
        //      "profiles": {
        //        "964ee5bb6cb7483ab6127f3cb7def662": {
        //          "displayName": "blue"
        //        }
        //      }
        //    },
        //    "51df2c5530b342c38582bf6271e5eedd": {
        //      "accessToken": "957f0c31c30442279f062f6a52aea35f",
        //      "username": "foo@gmail.com",
        //      "profiles": {
        //        "e80025c1b6ec4d7e92c1ca7aae20a10e": {
        //          "displayName": "papa"
        //        }
        //      }
        //    }
        //  },
        //  "launcherVersion": {
        //    "name": "2.0.805",
        //    "format": 20,
        //    "profilesFormat": 2
        //  },
        //  "settings": {
        //    "locale": "en-us",
        //    "showMenu": true
        //  },
        //  "analyticsToken": "b5786a69222a6a3cd38dca0a2813242f",
        //  "analyticsFailcount": 0,
        //  "selectedUser": {
        //    "account": "51df2c5530b342c38582bf6271e5eedd",
        //    "profile": "e80025c1b6ec4d7e92c1ca7aae20a10e"
        //  }
        //}

        public static bool hasMinecraftLauncherProfilesJson(JObject config)
        {
            return config["hosted_app_window"]["variables"] != null &&
                config["hosted_app_window"]["variables"]["load_selected_minecraft_profile_from_launcher_profiles_json"] != null;
        }

        private static JObject loadMinecraftLauncherProfilesJson(JObject config)
        {
            if (!hasMinecraftLauncherProfilesJson(config))
            {
                throw new Exception("must have launcher profile json file specified in config in order to load minecraft profile");
            }
            string path = GlobalSettings.substitute((string)config["hosted_app_window"]["variables"]["load_selected_minecraft_profile_from_launcher_profiles_json"]);
            Contract.Requires(File.Exists(path), "file not found: " + path);
            JObject lp = JObject.Parse(File.ReadAllText(path));
            Contract.Requires(lp["launcherVersion"] != null &&
                lp["launcherVersion"]["profilesFormat"] != null &&
                2 == (int)lp["launcherVersion"]["profilesFormat"],
                "This program only support Minecraft launcher profile v2.");
            return lp;
        }

        public static Dictionary<string, string> loadSelectedMinecraftProfileFromLauncherProfilesJson(JObject config)
        {
            JObject lp = loadMinecraftLauncherProfilesJson(config);

            // TODO: eliminate this by allowing login from this client
            Contract.Requires(lp["selectedUser"] != null &&
                lp["authenticationDatabase"] != null &&
                lp["authenticationDatabase"][lp["selectedUser"].ToString()] != null,
                "Minecraft launcher profile must have selected user. Have you logged into Minecraft yet?");

            JObject selectedProfile = (JObject)lp["authenticationDatabase"][lp["selectedUser"]["account"].ToString()];

            // flatten variables, for easy substitution. use profile v1 naming.
            Dictionary<string, string> result = new Dictionary<string, string>();
            result["accessToken"] = (string)selectedProfile["accessToken"];
            result["username"] = (string)selectedProfile["username"];
            result["displayName"] = (string)selectedProfile["profiles"][lp["selectedUser"]["profile"].ToString()]["displayName"];
            result["userid"] = lp["selectedUser"]["account"].ToString();
            return result;
        }
    }
}
