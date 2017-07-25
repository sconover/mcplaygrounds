import sys
import os


def _get_root_conf_value(key):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    contents = dict(line.strip().split('=') for line in open(os.path.join(this_dir,'root.conf')))
    value = contents[key]
    assert value!=None and len(value) > 0
    return value

def get_env_name():
    return _get_root_conf_value('env_name')

def get_minecraft_player_name():
    return _get_root_conf_value('minecraft_player_name')

def get_port():
    return int(_get_root_conf_value('port'))

def get_grpc_craft_port():
	return int(_get_root_conf_value('grpc_craft_port'))

sys.stderr.write("LOADING IPYTHON ENVIORNMENT {}: PLAYER={} PORT={}\n".format(get_env_name(), get_minecraft_player_name(), get_port()))
