import os, sys
this_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(this_dir, "..")
sys.path.append(parent_dir)
from root import *

c = get_config()
c.IPKernelApp.exec_lines = [
  "from oogway_client.oogway_client.turtle import *",
  "from grpccraft.world_metadata_pb2 import Material",
  "init('{}', {})".format(get_minecraft_player_name(), get_grpc_craft_port()),
  "%load_ext autoreload",
  "%autoreload 2",
  "import share"
]
