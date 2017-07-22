from lib.playground.util import *

def create_nginx_location_directives_for_bin_files(playground_config, absolute_bin_paths, nginx_conf_file, index_html_file):
    url_paths = []

    nginx_location_directives = ""
    for bin_path in absolute_bin_paths:
        url_path = "/" + playground_config.playground_name + "/" + bin_path.replace("/home/ubuntu/{}/".format(pdir(playground_config.playground_name)), "").replace("/", "__").replace("-", "_")
        url_paths.append(url_path)
        location_directive = \
            nginx_location_directive_for_executable(
                playground_config.playground_name,
                url_path,
                bin_path,
                "#bin")
        nginx_location_directives += location_directive

    rewrite_file_with_replace(nginx_conf_file, "# BIN_PATHS_GO_HERE", nginx_location_directives)

    bin_items = map(lambda u: "<li><a href=\"" + u + "\">" + u + "</a></li>", url_paths)
    rewrite_file_with_replace(index_html_file, "<!-- BIN_PATHS_GO_HERE -->", "<ul>\n" + "\n".join(bin_items) + "\n</ul>")

def nginx_location_directive_for_executable(playground_name, url_path, bin_path, redirect_url_relative_path):
    cmd = "sudo -u ubuntu " + bin_path
    redirect = playground_name + redirect_url_relative_path
    return "\n".join([
        "",
        "  location " + url_path + " {",
        "    content_by_lua 'ngx.log(ngx.STDERR, \"will run: " + cmd +
            " then will redirect to: " + redirect + "\");os.execute(\"" +
            cmd + "\");return ngx.redirect(\"/" +
            redirect + "\")';",
        "  }",
        ""
    ])

def reset_basic_auth_password(playground_name, password):
    ssh_exec("/usr/bin/htpasswd -b -c {}/htpasswd_file {} {}".format(
        pdir(playground_name),
        playground_name,
        password
    ))

def reload_nginx():
    ssh_exec("sudo /etc/init.d/nginx reload")
