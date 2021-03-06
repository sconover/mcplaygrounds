import os
import stat

from lib.core import ssh_exec, ssh_exec_all, ssh_get, scp_r, scp_r_remote_to_local, rsync_exec, ssh_tunnel
from lib.playground_config import PlaygroundConfig, load_playground_config

OVERLAY_STAGING_DIR = "/tmp/playground-staging"

def now_str():
    return time.strftime('%Y%m%d%H%M%S', time.localtime())

def pdir(playground_name):
    return "playgrounds/{}".format(playground_name)

def abs_pdir(playground_name):
    return "/home/ubuntu/playgrounds/{}".format(playground_name)

def write_executable_file(contents, path):
    f = open(path, 'w')
    f.write(contents)
    f.close()
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)

def write_bash_script(script_body_lines, path, bash_switches=" -ex"):
    bash_lines = [
        "#!/bin/bash{}".format(bash_switches),
        ""
    ]
    bash_lines.extend(script_body_lines)
    write_executable_file("\n".join(bash_lines), path)

def get_all_playground_config():
    all_config = {}
    json_lines = ssh_get("cat playgrounds/*/playground.json").split("\n")
    for line in json_lines:
        p = PlaygroundConfig()
        p.load_json(line)
        all_config[p.playground_name] = p
    return all_config

def rewrite_file_with_replace(path, search_for, replace_with):
    content = open(path).read()
    content = content.replace(search_for, replace_with)
    f = open(path, 'w')
    f.write(content)
    f.close()

def rewrite_file_with_multiline_regex_replace(path, regex, replace_with):
    content = open(path).read()
    content = re.sub(regex, replace_with, content, re.M | re.DOTALL)
    f = open(path, 'w')
    f.write(content)
    f.close()

def backup_dir_to_tmp(dir_to_backup):
    ssh_exec("d=/tmp/backup-before-rsync-`date +%Y-%m-%dT%H-%M-%S-%N` && if [ -d {} ]; then mkdir $d && cp -r {} $d; fi".format(dir_to_backup, dir_to_backup))

def rsync_destructive_be_careful_using_this(local_src_dir, remote_dest_dir):
    backup_dir_to_tmp(remote_dest_dir) # this is your get out of jail free card
    ssh_exec("mkdir -p {}".format(remote_dest_dir))
    rsync_exec(local_src_dir, remote_dest_dir, more_flags="--delete")

def rsync_nondestructive(local_src_dir, remote_dest_dir):
    ssh_exec("mkdir -p {}".format(remote_dest_dir))
    rsync_exec(local_src_dir, remote_dest_dir)

def set_directory_execute(playground_name):
    ssh_exec("find {} -type d | xargs chmod a+x".format(pdir(playground_name)))
