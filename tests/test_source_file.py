import tempfile
import unittest
from pathlib import Path

from reviewer.exceptions import (InvalidPythonSourceError,
                                 NotAPythonFileError,
                                 SourceFileNotFoundError)
from reviewer.source_file import SourceFile


class SourceFileTest(unittest.TestCase):
    def test_keeps_lines_of_valid_code(self):
        source_file = SourceFile("total = 1\nprint(total)\n")
        self.assertEqual(source_file.lines(), ["total = 1", "print(total)"])

    def test_invalid_code_raises_error_with_line_number(self):
        with self.assertRaises(InvalidPythonSourceError) as context:
            SourceFile("total = 1\nprint(total\n")
        self.assertEqual(context.exception.line_number, 2)

    def test_missing_file_raises_not_found(self):
        with self.assertRaises(SourceFileNotFoundError):
            SourceFile.from_path("this_file_does_not_exist.py")

    def test_non_python_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            text_file = Path(folder) / "notes.txt"
            text_file.write_text("hello", encoding="utf-8")
            with self.assertRaises(NotAPythonFileError):
                SourceFile.from_path(text_file)

    def test_reads_python_file_from_disk(self):
        with tempfile.TemporaryDirectory() as folder:
            python_file = Path(folder) / "sample.py"
            python_file.write_text("answer = 42\n", encoding="utf-8")
            source_file = SourceFile.from_path(python_file)
        self.assertEqual(source_file.lines(), ["answer = 42"])


if __name__ == "__main__":
    unittest.main()
