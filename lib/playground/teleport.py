import os

from lib.core import ssh_exec, ssh_exec_all, ssh_get, scp_r, scp_r_remote_to_local
from lib.playground.util import *

class TeleportAction(): # struct style, in keeping with the rest of this file
    def __init__(self, server_playground_name, player_name, destination_label, x, y, z):
        self.server_playground_name = server_playground_name
        self.player_name = player_name
        self.destination_label = destination_label
        self.x = x
        self.y = y
        self.z = z

def all_accessible_teleport_actions(playground_config):
    actions = []
    all_config = get_all_playground_config()
    for playground_name in all_config:
        c = all_config[playground_name]

        if c.teleport_destinations is not None \
        and len(c.teleport_destinations) > 0 \
        and playground_config.playground_name in c.teleport_destinations:
            for destination_label in c.teleport_destinations[playground_config.playground_name]:
                destination_coordinates = c.teleport_destinations[playground_config.playground_name][destination_label]
                mc_server_playground_name = playground_config.playground_name
                player_name = c.initial_minecraft_player_name_for_oogway
                x = destination_coordinates["x"]
                y = destination_coordinates["y"]
                z = destination_coordinates["z"]
                actions.append(TeleportAction(mc_server_playground_name, player_name, destination_label, x, y, z))
    return actions

def bash_fragment_teleport(teleport_action):
    server_playground_name = teleport_action.server_playground_name
    player_name = teleport_action.player_name
    destination_label = teleport_action.destination_label
    x = teleport_action.x
    y = teleport_action.y
    z = teleport_action.z
    return "\n".join([
        "",
        "tmux send -t {server_playground_name}-mc \"tp {player_name} {x} {y} {z}\" ENTER",
        "tmux send -t {server_playground_name}-mc \"spawnpoint {player_name} {x} {y} {z}\" ENTER",
        "echo \"teleported {player_name} to {destination_label}=({x},{y},{z}) in minecraft server {server_playground_name}-mc\"",
        ""
    ]).format(**locals())

def create_game_commands(playground_config, nginx_conf_file, index_html_file):
    # TODO?: pull gamemode/spectator changes into here

    game_bin_dir = OVERLAY_STAGING_DIR + "/bin/game"
    os.makedirs(game_bin_dir)

    destination_to_actions = {}
    for teleport_action in all_accessible_teleport_actions(playground_config):
        if teleport_action.destination_label not in destination_to_actions:
            destination_to_actions[teleport_action.destination_label] = []
        destination_to_actions[teleport_action.destination_label].append(teleport_action)

    for destination in sorted(destination_to_actions.keys()):
        if len(destination_to_actions[destination])==1:
            continue

        teleport_bash_lines = [
            "#!/bin/bash -ex",
            ""
        ]
        for teleport_action in destination_to_actions[destination]:
            teleport_bash_lines.append(bash_fragment_teleport(teleport_action))
        file_name = "group_teleport_to__" + destination + "__" + str(len(destination_to_actions[destination])) + "_players"
        path = game_bin_dir + "/" + file_name
        write_executable_file("\n".join(teleport_bash_lines), path)

    for teleport_action in all_accessible_teleport_actions(playground_config):
        teleport_bash = "\n".join([
            "#!/bin/bash -ex",
            "",
            bash_fragment_teleport(teleport_action)
        ])
        file_name = "teleport__" + teleport_action.player_name + "__to__" + teleport_action.destination_label
        path = game_bin_dir + "/" + file_name
        write_executable_file(teleport_bash, path)
