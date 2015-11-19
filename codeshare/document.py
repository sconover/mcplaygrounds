import ast
import glob
import os

def gen_simple_html_documentation(code_dir, target_html_file):
    doc_lines = []

    paths = glob.glob(code_dir + "/*.py")
    for path in sorted(paths):
        module = ast.parse(open(path).read())
        module_name_added = False
        module_name = os.path.basename(path).replace(".py", "")
        for child in module.body:
            if isinstance(child, ast.FunctionDef) and ast.get_docstring(child)!=None:
                if not module_name_added:
                    doc_lines.append("<h2>" + module_name + "</h2>")
                    module_name_added = True
                function_name = module_name + "." + child.name + \
                    "(" + ",".join(map(lambda a: a.id, child.args.args)) + ")"
                html_docstring = ast.get_docstring(child).replace("\n", "<br/>")
                doc_lines.append("<p><b><pre>" + function_name.strip() + "</b> " + html_docstring + "</pre>")

    f = open(target_html_file, "w")
    f.write("\n".join(doc_lines))
    f.close()

if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.realpath(__file__))
    gen_simple_html_documentation(os.path.join(this_dir, "test/samples/source"), "/tmp/testdoc.html")
