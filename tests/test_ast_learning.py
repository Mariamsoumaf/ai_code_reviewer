"""Learning tests (Clean Code, Chapter 8: Boundaries).

They check how the third-party boundary (Python's ast module) behaves.
If a new Python version changes ast, these tests fail first and show
exactly what changed.
"""

import ast
import unittest


class AstLearningTest(unittest.TestCase):
    def test_parse_keeps_line_numbers(self):
        tree = ast.parse("first = 1\nsecond = 2\n")
        second_assignment = tree.body[1]
        self.assertEqual(second_assignment.lineno, 2)

    def test_keyword_arguments_have_line_numbers(self):
        call = ast.parse("run('ls', shell=True)").body[0].value
        keyword = call.keywords[0]
        self.assertEqual((keyword.arg, keyword.lineno), ("shell", 1))

    def test_f_string_becomes_joined_str(self):
        expression = ast.parse("f'SELECT {name}'").body[0].value
        self.assertIsInstance(expression, ast.JoinedStr)

    def test_invalid_code_raises_syntax_error_with_line(self):
        with self.assertRaises(SyntaxError) as context:
            ast.parse("good = 1\nbad = (\n")
        self.assertIsNotNone(context.exception.lineno)


if __name__ == "__main__":
    unittest.main()
