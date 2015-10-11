import os
import sys
import unittest

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_dir, "../"))

import extract

class UnitTest(unittest.TestCase):
    def test_find_functions(self):
        source_lines = [
            "def f1():",
            "    \"\"\"this is a docstring\"\"\"",
            "    return 1",
            "",
            "def f2():",
            "    f1()",
            "    return 2",
            "",
            "f2()",
            "x = 2+3",
            "",
            "def f3():",
            "    \"\"\"this is a docstring\"\"\"",
            "    wont_work_but_should_parse()"
        ]
        result = extract.find_functions_in_source_having_docstring("\n".join(source_lines))
        self.assertEqual([
            {"name": "f1", "start":0, "end":3},
            {"name": "f3", "start":11, "end":14}
        ], result)

    def test_find_functions_but_not_parseable(self):
        source_lines = [
            "def f1():",
            "    \"\"\"this is a docstring\"\"\"",
            "    this is not valie python code"
        ]

        with self.assertRaises(SyntaxError):
            extract.find_functions_in_source_having_docstring("\n".join(source_lines))

    def test_get_source_parts(self):
        source_lines = [
            "def f1():",
            "    \"\"\"this is a docstring\"\"\"",
            "    return 1",
            "",
            "def f2():",
            "    f1()",
            "    return 2",
            "",
            "f2()",
            "x = 2+3",
            "",
            "def f3():",
            "    \"\"\"this is a docstring\"\"\"",
            "    wont_work_but_should_parse()"
        ]
        result_str = extract.extract_source_parts("\n".join(source_lines), [
            {"name": "f1", "start":0, "end":3},
            {"name": "f3", "start":11, "end":14}
        ])

        expected_source_lines = [
            "def f1():",
            "    \"\"\"this is a docstring\"\"\"",
            "    return 1",
            "",
            "def f3():",
            "    \"\"\"this is a docstring\"\"\"",
            "    wont_work_but_should_parse()"
        ]
        self.assertEqual("\n".join(expected_source_lines) + "\n", result_str)

if __name__ == '__main__':
    unittest.main()
