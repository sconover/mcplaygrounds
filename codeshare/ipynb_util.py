import IPython.nbconvert
import extract
import glob
import datetime

def ipynb_to_python_source_str(ipynb_file):
    exporter =  IPython.nbconvert.PythonExporter()
    output, _ = exporter.from_filename(ipynb_file)
    return output.replace("# coding: utf-8", "")

def extract_functions_from_ipynb_files(glob_path):
    result_str = ""
    paths = glob.glob(glob_path)
    for path in sorted(paths):
        ipynb_python_source_str = ipynb_to_python_source_str(path)
        result_str += "# === functions from {} ===\n\n".format(path)
        print "# === functions from {} ===\n\n".format(path)
        result_str += extract.extract_source_parts(ipynb_python_source_str, extract.find_functions_in_source_having_docstring(ipynb_python_source_str))
        result_str += "\n\n\n\n"
    return result_str

def extract_functions_from_ipynb_files_and_write_to_file_if_successful(glob_path, target_python_file):
    try:
        content = "\n".join([
            "import sys",
            "import os",
            "import importlib",
            "",
            "this_dir = os.path.dirname(os.path.realpath(__file__))",
            "sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), \"../../lib\"))",
            "",
            "local_files = [f for f in os.listdir(this_dir) if f.endswith('.py') and os.path.basename(__file__) != f and not f.startswith('_')]",
            "module_names = map(lambda f: f.replace('.py', ''), local_files)",
            "for m in module_names:",
            "    globals()[m] = importlib.import_module(m)",
            "",
            "from mcgamedata import block, living",
            "from oogway.turtle import *",
            ""
        ])
        content += extract_functions_from_ipynb_files(glob_path)
        f = open(target_python_file, "w")
        f.write(content)
        f.close()
        print "updated {} at {}".format(target_python_file, datetime.datetime.now())
    except Exception as e:
        print "did not update {} because '{}' at {}".format(target_python_file, e, datetime.datetime.now())
