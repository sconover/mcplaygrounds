import ast
import os

def find_functions_in_source(python_source_str):
    function_locations = []
    for child in ast.parse(python_source_str).body:
        if len(function_locations) > 0 and "end" not in function_locations[-1]:
            function_locations[-1]["end"] = child.lineno - 2
        if isinstance(child, ast.FunctionDef):
            function_locations.append({"name":child.name, "start":child.lineno - 1})
    if len(function_locations) > 0 and "end" not in function_locations[-1]:
        function_locations[-1]["end"] = len(python_source_str.split("\n"))
    return function_locations

def extract_source_parts(source_str, snippets):
    source_lines = source_str.split("\n")
    result_lines = []
    for snippet in snippets:
        result_lines.extend(source_lines[snippet["start"]:snippet["end"]])
        result_lines.append("")
    return "\n".join(result_lines)
