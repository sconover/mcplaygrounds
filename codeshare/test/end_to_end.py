import os
import sys
import unittest

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_dir, "../"))

import ipynb_util
import codeshare

# ipynb_python_source_str = ipynb_util.ipynb_to_python_source_str(os.path.join(this_dir, "samples/sample.ipynb"))
# print ipynb_python_source_str
# print codeshare.extract_source_parts(ipynb_python_source_str, codeshare.find_functions_in_source(ipynb_python_source_str))

print ipynb_util.extract_functions_from_ipynb_files(os.path.join(this_dir, "samples/*.ipynb"))

ipynb_util.extract_functions_from_ipynb_files_and_write_to_file_if_successful(os.path.join(this_dir, "samples/*.ipynb"), "/tmp/foo.py")
