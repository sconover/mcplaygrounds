import os
from string import Template

from lib.playground.util import *

def convert_markdown_to_ipython_notebook(markdown_file):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    template_relative_path = os.path.join(this_dir, "../../template/ipython.markdown.template")
    markdown_string_array = map(lambda line: '"' + line + '\\n"', open(markdown_file).read().split("\n"))
    markdown_string_array = ",\n".join(markdown_string_array)
    ipython_markdown = Template(open(template_relative_path).read()).substitute({"markdown_string_array": markdown_string_array})
    data_dir = os.path.join(OVERLAY_STAGING_DIR, "ipython-notebook-root/data")
    os.makedirs(data_dir)
    ipython_markdown_file = os.path.join(data_dir, os.path.basename(markdown_file).replace(".md", "") + ".ipynb")
    f = open(ipython_markdown_file, 'w')
    f.write(ipython_markdown)
    f.close()

def create_and_link_shared_dir(playground_config):
    ssh_exec("file ipython-share || mkdir ipython-share")
    ssh_exec("touch ipython-share/__init__.py")
    ssh_exec("ln -nsf /home/ubuntu/ipython-share {}/ipython-notebook-root/data/share".format(pdir(playground_config.playground_name)))
    this_dir = os.path.dirname(os.path.realpath(__file__))
    scp_r(this_dir + "/../../misc/data_share_init.py", "{}/ipython-notebook-root/data/share/__init__.py".format(pdir(playground_config.playground_name)))

def create_and_link_shared2_dir(playground_config):
    ssh_exec("file ipython-share2 || mkdir ipython-share2")
    ssh_exec("touch ipython-share2/__init__.py")
    ssh_exec("ln -nsf /home/ubuntu/ipython-share2 {}/ipython-notebook-root/data/share2".format(pdir(playground_config.playground_name)))

def create_and_link_share_file(playground_config):
    ssh_exec("ln -nsf /home/ubuntu/share.py {}/ipython-notebook-root/data/share.py".format(pdir(playground_config.playground_name)))

def create_and_link_all_notebook_dir(playground_config):
    ssh_exec("file ipython-all || mkdir ipython-all")
    ssh_exec("ln -nsf /home/ubuntu/playgrounds/{}/ipython-notebook-root/data /home/ubuntu/ipython-all/{}".format(playground_config.playground_name, playground_config.playground_name))
    if playground_config.is_all_notebook:
        ssh_exec("ln -nsf /home/ubuntu/ipython-all /home/ubuntu/playgrounds/{}/ipython-notebook-root/data/all".format(playground_config.playground_name, playground_config.playground_name))

def grpc_craft_python_client_lib_dir(playground_name):
    return ipython_lib_dir(playground_name) + "/oogway_client"

def ipython_lib_dir(playground_name):
    return "{}/ipython-notebook-root/lib".format(pdir(playground_name))

def ipython_data_dir(playground_name):
    return "{}/ipython-notebook-root/data".format(pdir(playground_name))

def quick_backup_ipython_notebooks(playground_name):
    backup_dir = os.path.join("ipython_quick_backups", time.strftime("%Y%m%dT%H%M%S") + "-" + playground_name)
    backup_ipython_notebooks(playground_name, backup_dir)

def backup_ipython_notebooks(playground_name, ipython_data_backup_dir):
    print("backing up {} ipython notebooks to {}".format(playground_name, ipython_data_backup_dir))
    ssh_exec_all([
        "mkdir -p " + ipython_data_backup_dir,
        "cp -r " + ipython_data_dir(playground_name) + "/* " + ipython_data_backup_dir + "/"
    ])

def write_ipython_notebook_html():
    scp_r("template/notebook.html.template", ".python-virtualenv/local/lib/python2.7/site-packages/IPython/html/templates/notebook.html")

