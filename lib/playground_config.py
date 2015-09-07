from lib.core import BaseSettingsClass, load_config

class PlaygroundConfig(BaseSettingsClass):
    def __init__(self):
        self.playground_name = None
        self.minecraft_server_port = None
        self.minecraft_gamemode = None
        self.minecraft_force_gamemode = None
        self.minecraft_spawn_monsters = None
        self.minecraft_player_idle_timeout = None
        self.minecraft_announce_player_achievements = None
        self.minecraft_whitelist = None
        self.minecraft_whitelist_json = None
        self.raspberry_juice_sponge_plugin_port = None
        self.ipython_notebook_server_http_port = None
        self.web_password = None
        self.initial_minecraft_player_name_for_oogway = None
        self.fully_qualified_domain_name = None
        self.help_instructions = None
        self.usb_stick_howto_url = None
        self.usb_stick_dir = None
        self.minecraft_reference_launcher_profile_json_file = None
        self._freeze() # no more attribute definitions are allowed

DEFAULT_CONFIG = PlaygroundConfig()
DEFAULT_CONFIG.minecraft_gamemode = 1 # creative
DEFAULT_CONFIG.minecraft_force_gamemode = True
DEFAULT_CONFIG.minecraft_spawn_monsters = False
DEFAULT_CONFIG.minecraft_player_idle_timeout = 1440 # 1 day
DEFAULT_CONFIG.minecraft_announce_player_achievements = False # annoying
DEFAULT_CONFIG.minecraft_whitelist = True
DEFAULT_CONFIG.minecraft_whitelist_json = "[]"

def load_playground_config(playground_name, config_path):
    return load_config(playground_name, PlaygroundConfig, DEFAULT_CONFIG, 'playground_name', config_path)
