from lib.playground.util import *

def spigot_dir_for_playground(playground_name):
    return "{}/spigot-server".format(abs_pdir(playground_name))

def spigot_executable_root_dir_for_playground(playground_name):
    return "{}/spigot-server/bin".format(abs_pdir(playground_name))

def spigot_jar_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/spigot.jar"

def grpc_craft_properties_abs_path(playground_name):
    return spigot_dir_for_playground(playground_name) + "/grpc_craft.properties"

def grpc_craft_plugin_jar_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/plugins/grpc-craft-plugin.jar"

def copy_spigot_server_files(playground_name):
    d = spigot_dir_for_playground(playground_name)
    j = spigot_jar_for_playground(playground_name)
    ssh_exec("mkdir -p {} && cp `{}` {}".format(d, const.SPIGOT_LATEST_JAR_LOCATOR_COMMAND, j))

def spigot_server_startup_java_command(playground_config):
	# There MUST be agreement between the grpc system property name and 
	# properties file contents in this project, and what the application expects
	return "java -Xmx8g -Xms256m " + \
		"-Dgrpccraft.properties.path={} ".format(grpc_craft_properties_abs_path(playground_config.playground_name)) + \
		"-Djava.net.preferIPv4Stack=true " + \
		"-XX:-UsePerfData -XX:+UseConcMarkSweepGC " + \
		"-XX:PermSize=256m -XX:MaxPermSize=256m " + \
		"-XX:+PrintAdaptiveSizePolicy -verbose:gc -XX:+PrintGCDetails " + \
		"-XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps -XX:+PrintTenuringDistribution " + \
		"-Xloggc:spigot-jvm-gc.log " + \
		"-jar spigot.jar"