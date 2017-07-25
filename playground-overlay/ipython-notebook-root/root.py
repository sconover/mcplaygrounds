import sys
import os
import subprocess

this_dir = os.path.dirname(os.path.realpath(__file__))

def _get_root_conf_value(key):
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

def nginx_conf_content():
        lines = [
            "location /programs/{}/ {{".format(get_env_name()), # double {{ to escape for interpolation
            "  proxy_pass http://127.0.0.1:{};".format(get_port()),
            "  proxy_http_version 1.1;",
            "  proxy_set_header Upgrade $http_upgrade;",
            "  proxy_set_header Connection \"upgrade\";",
            "  proxy_set_header Origin \"\";",
            "}"
        ]
        return "\n".join(lines) + "\n\n"

sys.stderr.write("local nginx.conf:\n")
sys.stderr.write(nginx_conf_content())

def write_nginx_conf():
    nginx_conf_path = os.path.join(this_dir,'nginx.conf')
    f = open(nginx_conf_path, 'w')
    f.write(nginx_conf_content())
    f.close()

write_nginx_conf()

def reload_nginx():
    print(subprocess.check_output("sudo /etc/init.d/nginx reload 2>&1", shell=True))

reload_nginx()
