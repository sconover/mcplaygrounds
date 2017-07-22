from lib.core import ssh_exec, ssh_exec_all, ssh_get, scp_r, scp_r_remote_to_local

from lib.playground.util import *

def prepare_client_log(playground_name):
    ssh_exec_all([
        # Create a file for client logging that's owned by (and thus writeable by) the
        # same unix user that nginx workers run as.
        # There must be agreement between this path and the path in the playground's nginx.conf.
        "touch {}/client.log".format(pdir(playground_name)),
        "sudo chown www-data {}/client.log".format(pdir(playground_name))
    ])

def prepare_console_log(playground_name):
    ssh_exec_all([
        # Create a log dir to contains "tee's" of all console logs
        "mkdir -p {}/tmux_console_logs".format(pdir(playground_name))
    ])

def get_tmux_console_log_files():
    # get all executable files in all playground bin/tmux dirs, absolute paths
    return ssh_get("find playgrounds/*/tmux_console_logs/*.log -type f | xargs -r -L 1 readlink -f").strip().split("\n")

def rsyslog_monitor_conf_lines(label, log_path, facility):
    # I tried using the "modern" config, but it's buggy - the
    # facility option (local6) was being ignored.
    return [
        "",
        "$InputFileName {}".format(log_path),
        "$InputFileTag {}:".format(label),
        "$InputFileStateFile {}-log-state".format(label),
        "$InputFileSeverity info",
        "$InputFileFacility {}".format(facility),
        "$InputRunFileMonitor",
        "$InputFilePollInterval 1"
    ]

def write_rsyslog_conf(args):
    rsyslog_conf_lines = [
        "local5.* /var/log/server.log",
        "local6.* /var/log/client.log",
        "",
        "$ModLoad imfile"
    ]
    all_config = get_all_playground_config()
    for playground_name in all_config:
        rsyslog_conf_lines.extend(
            rsyslog_monitor_conf_lines(
                playground_name + "-client",
                "/home/ubuntu/playgrounds/{}/client.log".format(playground_name),
                "local6"))

    rsyslog_conf_lines.extend(rsyslog_monitor_conf_lines("nginx-access", "/var/log/nginx/access.log", "local5"))
    rsyslog_conf_lines.extend(rsyslog_monitor_conf_lines("nginx-error", "/var/log/nginx/error.log", "local5"))

    # go look for all tmux console logs and monitor them
    for f in get_tmux_console_log_files():
        label = os.path.basename(f).replace(".log", "")
        rsyslog_conf_lines.extend(rsyslog_monitor_conf_lines(label, f, "local5"))

    playground_config = load_playground_config(args.playground_name, args.playground_config_file)
    loggly = [
        "",
        "# send above logging to loggly",
        "$WorkDirectory /var/spool/rsyslog # where to place spool files",
        "$ActionQueueFileName fwdRule1     # unique name prefix for spool files",
        "$ActionQueueMaxDiskSpace 1g       # 1gb space limit (use as much as possible)",
        "$ActionQueueSaveOnShutdown on     # save messages to disk on shutdown",
        "$ActionQueueType LinkedList       # run asynchronously",
        "$ActionResumeRetryCount -1        # infinite retries if host is down",
        "",
        'template(name="LogglyFormat" type="string" string="<%pri%>%protocol-version% %timestamp:::date-rfc3339% %HOSTNAME% %app-name% %procid% %msgid% [{}@41058] %msg%\\n")'.format(playground_config.loggly_token),
        "",
        'local5.*;local6.* action(type="omfwd" protocol="tcp" target="logs-01.loggly.com" port="514" template="LogglyFormat")'
    ]
    rsyslog_conf_lines.extend(loggly)

    f = open("/tmp/90-playground-rsyslog.conf", 'w')
    f.write("\n".join(rsyslog_conf_lines) + "\n")
    f.close()
    scp_r("/tmp/90-playground-rsyslog.conf", "/tmp/90-playground-rsyslog.conf")
    ssh_exec_all([
        "sudo mv /tmp/90-playground-rsyslog.conf /etc/rsyslog.d/90-playground-rsyslog.conf",
        "sudo pkill rsyslogd" # init.d force-reload, restart, stop, etc seem to do nothing. ugh.
    ])
