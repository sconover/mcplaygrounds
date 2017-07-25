import shutil
import os
from string import Template
import jsonschema
import simplejson
import oogway

this_dir = os.path.dirname(os.path.realpath(__file__))

NATIVE_CLIENT_CONFIG_SCHEMA = simplejson.loads(open(this_dir + "/../../schema/native-client-config-schema.json").read())

from lib import const
from lib.core import ssh_exec, ssh_exec_all, ssh_get, scp_r, scp_r_remote_to_local

from lib.playground.ipython import *
from lib.playground.nginx import *
from lib.playground.process_management import *
from lib.playground.teleport import *
from lib.playground.util import *

def validate_files(root_dir):
    validator = jsonschema.Draft3Validator(NATIVE_CLIENT_CONFIG_SCHEMA)

    for dirpath, dnames, fnames in os.walk(root_dir):
        for f in fnames:
            path = os.path.join(dirpath, f)
            if (path.endswith(".client-config.json")):
                validator.validate(simplejson.loads(open(path).read()))

def get_bin_files_on_server_and_staged(playground_config):
    bin_files_from_server = ssh_get("find {} -type f -executable | xargs -r -L 1 readlink -f".format(pdir(playground_config.playground_name))).strip().split("\n")

    bin_files_from_stage_dir = []
    for dirpath, dnames, fnames in os.walk(OVERLAY_STAGING_DIR + "/bin"):
        for f in fnames:
            bin_files_from_stage_dir.append(dirpath + "/" + f)

    bin_files_from_stage_dir_as_will_be_on_server = \
        map(lambda path: path.replace(OVERLAY_STAGING_DIR, "/home/ubuntu/" + pdir(playground_config.playground_name)), bin_files_from_stage_dir)

    all_absolute_bin_paths = []
    all_absolute_bin_paths.extend(bin_files_from_server)
    all_absolute_bin_paths.extend(bin_files_from_stage_dir_as_will_be_on_server)
    all_absolute_bin_paths = sorted(list(set(all_absolute_bin_paths)))
    return all_absolute_bin_paths

def evaluate_and_replace_templates(root_dir, template_vars):
    for dirpath, dnames, fnames in os.walk(root_dir):
        for f in fnames:
            path = os.path.join(dirpath, f)
            if (path.endswith(".template")):
                print("evaluate template: {}".format(path))
                new_file_content = Template(open(path).read()).substitute(template_vars)
                path_without_template_extension = os.path.splitext(path)[0]
                f = open(path_without_template_extension, 'w')
                f.write(new_file_content)
                f.close()
                os.remove(path)

def seed_staging_dir(staging_dir, overlay_dir, template_vars):
    shutil.rmtree(staging_dir, ignore_errors=True)
    shutil.copytree(overlay_dir, staging_dir)
    evaluate_and_replace_templates(staging_dir, template_vars)

def stage_overlay_files(playground_config):
    seed_staging_dir(OVERLAY_STAGING_DIR, "playground-overlay", playground_config.to_dict())
    playground_config.write_to_file("{}/playground.json".format(OVERLAY_STAGING_DIR))
    validate_files(OVERLAY_STAGING_DIR)
    create_game_commands(playground_config, OVERLAY_STAGING_DIR + "/nginx.conf", OVERLAY_STAGING_DIR + "/webroot/index.html")
    stage_start_bin(playground_config)
    create_nginx_location_directives_for_bin_files(
        playground_config,
        get_bin_files_on_server_and_staged(playground_config),
        OVERLAY_STAGING_DIR + "/nginx.conf",
        OVERLAY_STAGING_DIR + "/webroot/index.html")

def stage_generated_files(playground_config):
    oogway_docs_dir = os.path.join(os.path.dirname(oogway.__file__), "../docs")
    convert_markdown_to_ipython_notebook(os.path.join(oogway_docs_dir, "blocks.md"))

def clean_remote_dirs(playground_name):
    ssh_exec("rm -rf {}/bin/game".format(pdir(playground_name)))

def upload_staged_files(playground_name):
    rsync_nondestructive(OVERLAY_STAGING_DIR + "/", pdir(playground_name) + "/")
    print("Now, cleaning of the playground bin/ tree...")
    rsync_destructive_be_careful_using_this(OVERLAY_STAGING_DIR + "/bin/", pdir(playground_name) + "/bin/")