from lib.core import BaseSettingsClass, load_config

class PlaygroundConfig(BaseSettingsClass):
    def __init__(self):
        self.playground_name = None
        self.minecraft_server_port = None
        self.minecraft_server_jvm_debug_port = None
        self.minecraft_server_variant = None
        self.minecraft_gamemode = None
        self.minecraft_force_gamemode = None
        self.minecraft_spawn_monsters = None
        self.minecraft_player_idle_timeout = None
        self.minecraft_announce_player_achievements = None
        self.minecraft_whitelist = None
        self.minecraft_whitelist_json = None
        self.minecraft_startup_commands = None
        self.raspberry_juice_sponge_plugin_port = None
        self.grpc_craft_port = None
        self.grpc_craft_admin_web_port = None
        self.grpc_craft_jupyter_notebook_support_web_port = None
        self.grpc_craft_prometheus_metrics_scrape_web_port = None
        self.sentry_io_client_key_aka_dsn = None
        self.circle_ci_api_token = None
        self.jupyter_notebook_readwrite_aws_s3_access_key = None
        self.jupyter_notebook_readwrite_aws_s3_secret_key = None
        self.jupyter_notebook_readonly_aws_s3_access_key = None
        self.jupyter_notebook_readonly_aws_s3_secret_key = None
        self.jupyter_notebook_aws_s3_region = None
        self.jupyter_notebook_aws_s3_bucket = None
        self.ipython_notebook_server_http_port = None
        self.ipython_notebook_server_http_port = None
        self.web_password = None
        self.initial_minecraft_player_name_for_oogway = None
        self.fully_qualified_domain_name = None
        self.help_instructions = None
        self.lesson_url = None
        self.usb_stick_howto_url = None
        self.usb_stick_dir = None
        self.minecraft_reference_launcher_profile_json_file = None
        self.loggly_token = None
        self.personal_x_1 = None
        self.personal_z_1 = None
        self.personal_x_2 = None
        self.personal_z_2 = None
        self.teleport_destinations = None
        self.is_all_notebook = None
        self._freeze() # no more attribute definitions are allowed

DEFAULT_CONFIG = PlaygroundConfig()
DEFAULT_CONFIG.minecraft_gamemode = 1 # creative
DEFAULT_CONFIG.minecraft_force_gamemode = True
DEFAULT_CONFIG.minecraft_spawn_monsters = False
DEFAULT_CONFIG.minecraft_player_idle_timeout = 1440 # 1 day
DEFAULT_CONFIG.minecraft_announce_player_achievements = False # annoying
DEFAULT_CONFIG.minecraft_whitelist = True
DEFAULT_CONFIG.minecraft_whitelist_json = "[]"
DEFAULT_CONFIG.minecraft_startup_commands = []
DEFAULT_CONFIG.teleport_destinations = {}
DEFAULT_CONFIG.minecraft_server_port = False
DEFAULT_CONFIG.minecraft_server_jvm_debug_port = False
DEFAULT_CONFIG.raspberry_juice_sponge_plugin_port = False
DEFAULT_CONFIG.grpc_craft_port = False
DEFAULT_CONFIG.grpc_craft_admin_web_port = False
DEFAULT_CONFIG.grpc_craft_jupyter_notebook_support_web_port = False
DEFAULT_CONFIG.grpc_craft_prometheus_metrics_scrape_web_port = False
DEFAULT_CONFIG.sentry_io_client_key_aka_dsn = False
DEFAULT_CONFIG.jupyter_notebook_readwrite_aws_s3_access_key = None
DEFAULT_CONFIG.jupyter_notebook_readwrite_aws_s3_secret_key = None
DEFAULT_CONFIG.jupyter_notebook_readonly_aws_s3_access_key = None
DEFAULT_CONFIG.jupyter_notebook_readonly_aws_s3_secret_key = None
DEFAULT_CONFIG.jupyter_notebook_aws_s3_region = None
DEFAULT_CONFIG.jupyter_notebook_aws_s3_bucket = None
DEFAULT_CONFIG.minecraft_server_variant = "sponge_mcpi" # also, "spigot_grpc"
DEFAULT_CONFIG.personal_x_1 = 0
DEFAULT_CONFIG.personal_z_1 = 0
DEFAULT_CONFIG.personal_x_2 = 0
DEFAULT_CONFIG.personal_z_2 = 0
DEFAULT_CONFIG.ipython_notebook_server_http_port = False
DEFAULT_CONFIG.is_all_notebook = False

def load_playground_config(playground_name, config_path):
    return load_config(playground_name, PlaygroundConfig, DEFAULT_CONFIG, 'playground_name', config_path)
