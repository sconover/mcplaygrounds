import os.path
import subprocess
import sys
import json

def settings_path():
  home = os.path.expanduser("~")
  return os.path.join(home, '.mc-class-server-ec2.json')

def save_settings(new_settings):
  json_settings_str = json.dumps(new_settings, sort_keys=True, indent=2, separators=(',', ': '))
  f = open(settings_path(), 'w')
  f.write(json_settings_str + "\n")
  f.close()

def load_settings():
  settings_not_found_exception = Exception(
      "Required ec2 settings not found. " +
      "Please run 'server use --help' for information about what must be set up.")

  if os.path.isfile(settings_path()) != True:
    raise settings_not_found_exception

  settings = json.loads(open(settings_path()).read())

  if 'ec2_private_key_file' not in settings or \
    'ec2_user' not in settings or \
    'ec2_host' not in settings:
    raise settings_not_found_exception

  return settings

def ssh_exec_all(commands):
  ssh_exec(" && ".join(commands))

def ssh_command_parts(remote_command):
  settings = load_settings()
  user_at_host = "{}@{}".format(settings['ec2_user'], settings['ec2_host'])
  parts = [
    'ssh', '-i', settings['ec2_private_key_file'],
    user_at_host,
    remote_command
  ]
  return parts

def ssh_exec(remote_command):
  parts = ssh_command_parts(remote_command)
  cmd = " ".join(parts)
  print "> {}".format(cmd)
  sys.stderr.write("< ")
  if subprocess.call(parts)!=0:
    raise Exception("FAILED: {}".format(cmd))

def ssh_get(remote_command):
  return subprocess.check_output(ssh_command_parts(remote_command)).strip()
