import os

from lib import const
from lib.playground.spigot_grpc import *

def tmux_kill_command(session_name):
    # tmux sends sighup (weird), which I believe is responsible for java sometimes
    # outliving its tmux session parent.
    # so, send sigterm to children of session, before running tmux kill-session
    return "tmux list-panes -s -F '#{pane_pid}' -t " + session_name + " | xargs -r kill; tmux kill-session -t " + session_name + " || true"

def tmux_kill(session_name):
    if does_tmux_session_exist(session_name):
        ssh_exec(tmux_kill_command(session_name))
    else:
        print("tmux session '{}' not found, doing nothing.".format(session_name))

def tmux_start(playground_name, session_suffix, script_name):
    session_name = playground_name + session_suffix
    if does_tmux_session_exist(session_name):
        print("tmux session '{}' found, doing nothing.".format(session_name))
    else:
        ssh_exec(abs_tmux_start_script_path(playground_name, script_name))

def does_tmux_session_exist(session_name):
    output = ssh_get("tmux ls | egrep '^" + session_name + ": ' || true").strip()
    if session_name in output:
        return True
    else:
        return False

def tmux_new_session_command(working_dir, session_name, command):
    return "cd {} && /usr/bin/tmux new-session -s {} -d '{}'".format(working_dir, session_name, command)

# TODO: make this a top-level command

def tmux_playground_start_command(playground_name, subdir, tmux_session_suffix, command):
    return tmux_new_session_command(
                pdir(playground_name) + "/" + subdir,
                playground_name + "-" + tmux_session_suffix,
                command)

def at_reboot_tmux_crontab_line(playground_name, subdir, tmux_session_suffix, command):
    return "@reboot " + tmux_playground_start_command(playground_name, subdir, tmux_session_suffix, command)

def tmux_send_command(playground_name, command):
    return "tmux send -t " + playground_name + "-mc \"" + command + "\" ENTER"

def tmux_kill_bash_fragment(session_name):
    return "\n".join([
        "exit_code=$(tmux ls | egrep '^{}: ' > /dev/null; echo $?)".format(session_name),
        "",
        "if [ \"$exit_code\" = \"0\" ]; then",
        "  echo \"found {} session, killing...\"".format(session_name),
        "  " + tmux_kill_command(session_name),
        "else",
        "  echo \"no {} session found\"".format(session_name),
        "fi"
    ])

def tmux_new_session_command_no_cd(session_name, command, console_log_path):
    return "/usr/bin/tmux new-session -s {} -d '{} 2>&1 | tee -a {}'".format(session_name, command, console_log_path)

def tmux_playground_start_command_no_cd(playground_name, tmux_session_suffix, command):
    session_name = playground_name + "-" + tmux_session_suffix
    return tmux_new_session_command_no_cd(
                playground_name + "-" + tmux_session_suffix,
                command,
                abs_pdir(playground_name) + "/tmux_console_logs/" + session_name + ".log")

def relative_tmux_script_path(playground_name, script_name):
    return "/bin/tmux/{}".format(script_name)

def abs_tmux_start_script_path(playground_name, script_name):
    return "{}/bin/tmux/{}".format(abs_pdir(playground_name), script_name)

def write_playground_bash_script_to_staging_dir(script_body_lines, relative_path, bash_switches=" -ex"):
    path = OVERLAY_STAGING_DIR + relative_path
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    write_bash_script(script_body_lines, path, bash_switches=bash_switches)

def write_tmux_session_restart_script_to_staging_dir(playground_name, tmux_session_suffix, start_command, script_name, run_before=None):
    session_name = playground_name + "-" + tmux_session_suffix

    lines = [tmux_kill_bash_fragment(session_name)]

    if run_before!=None:
        lines.extend([
            "",
            run_before
        ])

    lines.extend([
        "",
        tmux_playground_start_command_no_cd(playground_name, tmux_session_suffix, start_command),
        ""
    ])
    write_playground_bash_script_to_staging_dir(lines, relative_tmux_script_path(playground_name, script_name))

def write_tmux_session_kill_script_to_staging_dir(playground_name, tmux_session_suffix, script_name):
    session_name = playground_name + "-" + tmux_session_suffix
    lines = [tmux_kill_bash_fragment(session_name)]
    write_playground_bash_script_to_staging_dir(lines, relative_tmux_script_path(playground_name, script_name))

def stage_start_bin(playground_config):
    if playground_config.minecraft_server_port:

        if playground_config.minecraft_server_variant not in [const.MINECRAFT_SERVER_VARIANT_SPONGE_MCPI, const.MINECRAFT_SERVER_VARIANT_SPIGOT_GRPC]:
            raise Exception( \
                "Every playground that runs a minecraft server " + \
                "MUST declare a valid variant. Actual: {}".format(playground_config.minecraft_server_variant))

        # minecraft start script and tmux restart script are intentionally named the same,
        # so that one replaces the other (depending on selected variant)

        variant_message = "echo 'STARTING VARIANT: {}'".format(playground_config.minecraft_server_variant)

        if playground_config.minecraft_server_variant == const.MINECRAFT_SERVER_VARIANT_SPONGE_MCPI:
            write_playground_bash_script_to_staging_dir([
                "cd {}/minecraft-server".format(abs_pdir(playground_config.playground_name)),
                variant_message,
                "exec java -Xmx2g -Xms1g -Djava.net.preferIPv4Stack=true -XX:-UsePerfData -XX:+UseConcMarkSweepGC -XX:PermSize=256m -XX:MaxPermSize=256m -XX:+PrintAdaptiveSizePolicy -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps -XX:+PrintTenuringDistribution -Xloggc:minecraft-jvm-gc.log -jar sponge-minecraft-server.jar run"
            ], "/bin/start/start_minecraft_server")

        if playground_config.minecraft_server_variant == const.MINECRAFT_SERVER_VARIANT_SPIGOT_GRPC:
            write_playground_bash_script_to_staging_dir([
                "pdir={}".format(abs_pdir(playground_config.playground_name)),
                "",
                "lsof -n -i4TCP:{} | grep LISTEN | awk '{{print $2}}' | xargs -L1 -r kill -9".format(playground_config.minecraft_server_port), # forcibly clean up possible leftover slop
                "",
                "# create symlinks to various directories under deployment/current - these files",
                "# are changed via application deployment",
                "mkdir -p $pdir/spigot-server/plugins",
                "ln -nsf $pdir/deployment/current/grpc-craft-plugin/grpc-craft-plugin.jar $pdir/spigot-server/plugins/grpc-craft-plugin.jar",
                "rm -rf $pdir/spigot-server/bin",
                "ln -nsf $pdir/deployment/current/grpc-craft-plugin/system_exec_bin $pdir/spigot-server/bin",
                "ln -sf $pdir/spigot-server/ipython-automation.properties $pdir/spigot-server/bin/ipython-automation.properties", # ugh, probably need some config/injection reform one of these days
                "ls -la $pdir/spigot-server",
                "ls -la $pdir/spigot-server/bin",
                "ls -la $pdir/spigot-server/bin/",
                "",
                "rm -rf $pdir/ipython-bootstrap",
                "mkdir -p $pdir/ipython-bootstrap/lib",
                "ln -nsf $pdir/deployment/current/grpc-craft-plugin/ipython_seed $pdir/ipython-bootstrap/seed",
                "ln -nsf $pdir/deployment/current/grpc-craft-plugin/python_oogway_client $pdir/ipython-bootstrap/lib/oogway_client",
                "ln -nsf $pdir/deployment/current/grpc-craft-plugin/python_jupyter_contents_manager_cloud_client $pdir/ipython-bootstrap/jupyter_contents_manager_cloud_client",
                "",
                "cd $pdir/spigot-server",
                "",
                "cd {}".format(spigot_dir_for_playground(playground_config.playground_name)),
                variant_message,
                "exec " + spigot_server_startup_java_command(playground_config)
            ], "/bin/start/start_minecraft_server")

        write_tmux_session_kill_script_to_staging_dir(playground_config.playground_name, "mc", "tmux_kill_minecraft_server")

        write_tmux_session_restart_script_to_staging_dir(
            playground_config.playground_name,
            "mc",
            "{}/bin/start/start_minecraft_server".format(abs_pdir(playground_config.playground_name)),
            "tmux_restart_minecraft_server")

def get_tmux_start_scripts():
    # get all executable files in all playground bin/tmux dirs, absolute paths
    return ssh_get("find playgrounds/*/bin/tmux -type f -executable | grep -v tmux_kill | xargs -r -L 1 readlink -f").strip().split("\n")
