import os
import sys
import unittest

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_dir, "../"))

import codeshare

class UnitTest(unittest.TestCase):
    def test_find_functions(self):
        source_lines = [
            "def f1():",
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
            "    wont_work_but_should_parse()"
        ]
        result = codeshare.find_functions_in_source("\n".join(source_lines))
        self.assertEqual([
            {"name": "f1", "start":0, "end":2},
            {"name": "f2", "start":3, "end":6},
            {"name": "f3", "start":10, "end":12}
        ], result)

    def test_find_functions_but_not_parseable(self):
        source_lines = [
            "def f1():",
            "    this is not valie python code"
        ]

        with self.assertRaises(SyntaxError):
            codeshare.find_functions_in_source("\n".join(source_lines))

    def test_get_source_parts(self):
        source_lines = [
            "def f1():",
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
            "    wont_work_but_should_parse()"
        ]
        result_str = codeshare.extract_source_parts("\n".join(source_lines), [
            {"name": "f1", "start":0, "end":2},
            {"name": "f2", "start":3, "end":6},
            {"name": "f3", "start":10, "end":12}
        ])

        expected_source_lines = [
            "def f1():",
            "    return 1",
            "",
            "def f2():",
            "    f1()",
            "    return 2",
            "",
            "def f3():",
            "    wont_work_but_should_parse()"
        ]
        self.assertEqual("\n".join(expected_source_lines) + "\n", result_str)

if __name__ == '__main__':
    unittest.main()
