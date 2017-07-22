from lib.playground.util import *

def spigot_dir_for_playground(playground_name):
    return "{}/spigot-server".format(abs_pdir(playground_name))

def spigot_jar_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/spigot.jar"

def grpc_craft_plugin_jar_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/plugins/grpc-craft-plugin.jar"

def copy_spigot_server_files(playground_name):
    d = spigot_dir_for_playground(playground_name)
    j = spigot_jar_for_playground(playground_name)
    ssh_exec("mkdir -p {} && cp `{}` {}".format(d, const.SPIGOT_LATEST_JAR_LOCATOR_COMMAND, j))

def spigot_server_startup_java_command(playground_config):
	return "java -Xmx8g -Xms1g " + \
		"-Dserver_id=SPIGOTGRPC_{} ".format(playground_config.playground_name) + \
		"-Dgrpc.port={} ".format(playground_config.grpc_craft_port) + \
		"-Djava.net.preferIPv4Stack=true " + \
		"-XX:-UsePerfData -XX:+UseConcMarkSweepGC " + \
		"-XX:PermSize=256m -XX:MaxPermSize=256m " + \
		"-XX:+PrintAdaptiveSizePolicy -verbose:gc -XX:+PrintGCDetails " + \
		"-XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps -XX:+PrintTenuringDistribution " + \
		"-Xloggc:spigot-jvm-gc.log " + \
		"-jar spigot.jar"