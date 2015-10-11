import ast
import glob

def gen_simple_html_documentation(code_dir):
    doc_lines = []

    paths = glob.glob(code_dir + "/*.py")
    for path in sorted(paths):
        module = ast.parse(open(path).read())
        for child in module.body:
            if isinstance(child, ast.FunctionDef) and ast.get_docstring(child)!=None:
                doc_lines.append(module.name + "." + child.name)
