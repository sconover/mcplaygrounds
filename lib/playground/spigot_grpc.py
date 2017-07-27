import os

from lib import const
from lib.playground.util import *

def grpc_craft_executable_root_dir_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/bin"

def spigot_dir_for_playground(playground_name):
    return "{}/spigot-server".format(abs_pdir(playground_name))

def spigot_jar_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/spigot.jar"

def grpc_craft_properties_abs_path(playground_name):
    return spigot_dir_for_playground(playground_name) + "/grpc_craft.properties"

def grpc_craft_plugin_jar_for_playground(playground_name):
    return spigot_dir_for_playground(playground_name) + "/plugins/grpc-craft-plugin.jar"

def grpc_craft_executable_root_dir_for_playground(playground_name):
	return spigot_dir_for_playground(playground_name) + "/bin"

def grpc_craft_ipython_seed_dir(playground_name):
    return os.path.join(abs_pdir(playground_name), const.IPYTHON_SEED_DIR)

def grpc_craft_ipython_user_libs_dir(playground_name):
    return os.path.join(abs_pdir(playground_name), const.IPYTHON_USER_LIBS_DIR)

def ipython_instance_root_dir(playground_name):
    return os.path.join(abs_pdir(playground_name), const.IPYTHON_INSTANCE_ROOT_DIR)

def ipython_url_path_prefix_for_playground(playground_name):
    return "/{}-programs".format(playground_name)

def get_ipython_bin_path():
    return "/home/ubuntu/{}/{}".format(const.PYTHON_VIRTUALENV, const.IPYTHON_BIN_PATH_DIR)


def copy_spigot_server_files(playground_name):
    d = spigot_dir_for_playground(playground_name)
    j = spigot_jar_for_playground(playground_name)
    e = grpc_craft_executable_root_dir_for_playground(playground_name)
    plugin_dest = grpc_craft_plugin_jar_for_playground(playground_name)
    ssh_exec("mkdir -p {} && cp `{}` {}".format(d, const.SPIGOT_LATEST_JAR_LOCATOR_COMMAND, j))
    ssh_exec("rm -f {} && cp `{}` {}".format(plugin_dest, const.GRPC_CRAFT_PLUGIN_JAR_LOCATOR_COMMAND, plugin_dest))
    ssh_exec("cp `{}`/* {}/".format(const.GRPC_CRAFT_BIN_DIR_LOCATOR_COMMAND, e))

    target_lib_dir = grpc_craft_ipython_user_libs_dir(playground_name)
    target_seed_dir = grpc_craft_ipython_seed_dir(playground_name)
    ssh_exec_all([
    	"rm -rf {} && mkdir -p {} && cp -R `{}` {}/".format(target_lib_dir, target_lib_dir, const.GRPC_CRAFT_PYTHON_CLIENT_DIR_LOCATOR_COMMAND, target_lib_dir),
    	"rm -rf {} && cp -R `{}` {}".format(target_seed_dir, const.GRPC_CRAFT_IPYTHON_SEED_LOCATOR_COMMAND, target_seed_dir),
    	"mkdir -p {}".format(ipython_instance_root_dir(playground_name))
    ])

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