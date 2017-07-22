CLIENT_CONFIG_TEMPLATE_DIR = "playground-overlay/webroot"
DEST_URL_BIN_PREP_DIR = "/tmp/playground-url-bin-dest"
SOURCE_URL_BIN_PREP_DIR = "/tmp/playground-url-bin-source"

# make client config template files and scripts on the server
# that allow us to signal to native clients that they should switch
# to the ipython notebook url for the ipynb file in question
def create_client_url_switch_scripts(source_playground_config, dest_playground_config, ipynb_relative_path):
    shutil.rmtree(DEST_URL_BIN_PREP_DIR, ignore_errors=True)
    os.makedirs(DEST_URL_BIN_PREP_DIR)
    shutil.rmtree(SOURCE_URL_BIN_PREP_DIR, ignore_errors=True)
    os.makedirs(SOURCE_URL_BIN_PREP_DIR)

    for dirpath, dnames, fnames in os.walk(CLIENT_CONFIG_TEMPLATE_DIR):
        for f in fnames:
            path = os.path.join(dirpath, f)
            if (path.endswith(".client-config.json.template")):
                client_config_name = "switch_client_browser_to_" + re.sub(r"[^A-Za-z0-9]+", "_", ipynb_relative_path) + "_" + f

                config = json.loads(open(path).read())
                # example: http://a.giantpurplekitty.com/foo/python/notebooks/Programming2.7%20-%20Putting%20it%20all%20together.ipynb
                config["browser_window"]["url"] = \
                    'http://${fully_qualified_domain_name}/${playground_name}/python/notebooks/' + \
                    urllib.quote(ipynb_relative_path)
                client_config_str = json.dumps(config, indent=2)
                fw = open(DEST_URL_BIN_PREP_DIR + "/" + client_config_name, 'w')
                fw.write(client_config_str)
                fw.close()

                # script for the playground we're copying TO, that makes this ipynb the
                # url the native client should load next time it polls for config changes.
                remote_config_path = client_config_name.replace(".template", "")
                remote_webroot_path = f.replace(".template", "")
                switch_to_url_bash = "\n".join([
                    "#/bin/bash -ex",
                    "",
                    "this_dir=$(dirname $0)",
                    "cp $this_dir/{} $this_dir/../../webroot/{}".format(remote_config_path, remote_webroot_path),
                    ""
                ])
                switch_url_script_file_name = client_config_name.replace(".client-config.json.template", "")
                write_executable_file(switch_to_url_bash, DEST_URL_BIN_PREP_DIR + "/" + switch_url_script_file_name)

                # script for the playground we're copying FROM, that will invoke all of
                # the individual scripts of this name...allowing us to change many different
                # playground urls at once.
                switch_all_script_name = switch_url_script_file_name.replace("switch_client_browser_to", "switch_all_client_browsers_to")
                switch_all_bash = "\n".join([
                    "#/bin/bash -ex",
                    "",
                    "this_dir=$(dirname $0)",
                    "find $this_dir/../../../*/bin/url/ -name {} | xargs -0 bash -c".format(switch_url_script_file_name),
                    ""
                ])
                write_executable_file(switch_all_bash, SOURCE_URL_BIN_PREP_DIR + "/" + switch_all_script_name)
    evaluate_and_replace_templates(DEST_URL_BIN_PREP_DIR, dest_playground_config.to_dict())
