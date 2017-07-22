def copy_minecraft_server_files(playground_name):
    ssh_exec("file {}/minecraft-server || (mkdir -p {}/minecraft-server && cp -R {}/. {}/minecraft-server/)".format(
        pdir(playground_name), pdir(playground_name), const.MINECRAFT_LATEST_DIR, pdir(playground_name)))

def minecraft_world_dir(playground_name):
    return "{}/minecraft-server/world".format(pdir(playground_name))
