"""Boundary around the file system and Python's ast module.

The rest of the reviewer never opens files or calls ast.parse directly,
so a change in those libraries only touches this class.
"""

import ast
from pathlib import Path

from reviewer.exceptions import (InvalidPythonSourceError,
                                 NotAPythonFileError,
                                 SourceFileNotFoundError)

PYTHON_EXTENSION = ".py"


class SourceFile:
    def __init__(self, text, name="<text>"):
        self._name = name
        self._lines = text.splitlines()
        self._tree = self._parse(text)

    @classmethod
    def from_path(cls, path):
        file_path = Path(path)
        if not file_path.is_file():
            raise SourceFileNotFoundError(file_path)
        if file_path.suffix != PYTHON_EXTENSION:
            raise NotAPythonFileError(file_path)
        return cls(file_path.read_text(encoding="utf-8"), str(file_path))

    @property
    def name(self):
        return self._name

    def lines(self):
        return list(self._lines)

    def nodes(self):
        return ast.walk(self._tree)

    def _parse(self, text):
        try:
            return ast.parse(text)
        except SyntaxError as error:
            raise InvalidPythonSourceError(self._name, error.lineno) from error
