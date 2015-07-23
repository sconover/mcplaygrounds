import os.path
import subprocess
import sys
import json

class BaseSettingsClass(object):
  __isfrozen = False
  def __setattr__(self, key, value):
      if self.__isfrozen and not hasattr(self, key):
          raise TypeError( "%r is a frozen class" % self )
      object.__setattr__(self, key, value)

  def _freeze(self):
      self.__isfrozen = True

  def to_dict(self):
    d = self.__dict__.copy()
    d.pop("_BaseSettingsClass__isfrozen", None)
    return d

  def to_json(self):
    return json.dumps(self.to_dict()) # intentionally all on one line

  def write_to_file(self, path):
    f = open(path, 'w')
    f.write(self.to_json() + "\n")
    f.close()

  def to_json(self):
    return json.dumps(self.to_dict()) # intentionally all on one line

  def load_json(self, json_str):
    self.load_dict(json.loads(json_str))

  def load_dict(self, d):
    for key in d:
      setattr(self, key, d[key])

  def merge_defaults(self, default_obj):
    for key in default_obj.__dict__:
      if getattr(self, key) == None:
        setattr(self, key, getattr(default_obj, key))

def load_configs_from_file(config_class, global_defaults, label_attr, config_path):
  label_to_config = {}
  json_struct = json.loads(open(config_path).read())
  defaults = config_class()
  defaults.load_dict(global_defaults)

  if "default" in json_struct:
    defaults.load_dict(json_struct["default"])
  json_struct.pop("default", None)

  for label in json_struct:
    config_struct = json_struct[label]
    config = config_class()
    setattr(config, label_attr, label)
    config.load_dict(config_struct)
    config.merge_defaults(defaults)
    for key in config.__dict__:
      if getattr(config, key) == None:
        raise Exception("Required key '{}' not found in config '{}'".format(
          key, label
        ))
    label_to_config[label] = config

  return label_to_config

def load_config(label, config_class, global_defaults, label_attr, config_path):
  label_to_config = load_configs_from_file(config_class, global_defaults, label_attr, config_path)
  if label not in label_to_config:
    raise Exception("Entry '{}' not found in config file '{}'".format(
      label, config_path
    ))
  return label_to_config[label]

class ServerConfig(BaseSettingsClass):
  def __init__(self):

    # here for the possibility of overriding in the server config file
    self.modern_gradle_apt_repo = "ppa:cwchien/gradle"
    self.modern_nginx_apt_repo = "ppa:nginx/stable"
    self.raspberry_juice_sponge_plugin_git_repo = "https://github.com/sconover/RaspberryJuiceSpongePlugin"
    self.ipython_git_repo = "https://github.com/ipython/ipython"
    self.mcpi_git_repo = "https://github.com/martinohanlon/mcpi"
    self.server_label = None

    # these MUST be specified in the separate server config file
    self.ssh_options = None
    self.user_at_host = None

    self._freeze() # no more attribute definitions are allowed

DEFAULT_CONFIG = ServerConfig()

def current_server_config_path():
  home = os.path.expanduser("~")
  return os.path.join(home, '.mc-current-server.json')

def set_current_server_config(server_label, server_config_file):
  server_config = load_config(server_label, ServerConfig, DEFAULT_CONFIG, 'server_label', server_config_file)
  server_config.write_to_file(current_server_config_path())

def load_current_server_config():
  server_config = ServerConfig()
  server_config.load_json(open(current_server_config_path()).read())
  return server_config

def ssh_exec_all(commands):
  ssh_exec(" && ".join(commands))

def ssh_command_parts(remote_command):
  server_config = load_current_server_config()
  return ['ssh', server_config.ssh_options, server_config.user_at_host, remote_command]

def ssh_exec(remote_command):
  parts = ssh_command_parts(remote_command)
  cmd = " ".join(parts)
  print "> {}".format(cmd)
  sys.stderr.write("< ")
  if subprocess.call(parts)!=0:
    raise Exception("FAILED: {}".format(cmd))

def ssh_get(remote_command):
  return subprocess.check_output(ssh_command_parts(remote_command)).strip()

def scp_r(local_path, remote_path):
  server_config = load_current_server_config()
  parts = [
    'scp', server_config.ssh_options, '-r',
    local_path,
    server_config.user_at_host + ":" + remote_path
  ]
  cmd = " ".join(parts)
  print "> {}".format(cmd)
  if subprocess.call(parts)!=0:
    raise Exception("FAILED: {}".format(cmd))
