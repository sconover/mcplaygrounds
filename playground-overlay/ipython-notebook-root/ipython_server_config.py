from root import *

c = get_config()

c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.port = get_port()
c.NotebookApp.ipython_dir = './'
c.NotebookApp.notebook_dir = './data'
c.NotebookApp.log_level = 'INFO'

# proxy-related settings
c.NotebookApp.base_url = "/{}/python/".format(get_env_name())
c.NotebookApp.trust_xheaders = True
c.NotebookApp.tornado_settings = {'static_url_prefix':"/{}/python/static/".format(get_env_name())}

import sys
import os

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_dir, "lib/codeshare"))
sys.path.append(os.path.join(this_dir, "data"))