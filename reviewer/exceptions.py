"""Errors the reviewer reports to the user instead of crashing."""


class ReviewError(Exception):
    """Base class for every expected error in the reviewer."""


class SourceFileNotFoundError(ReviewError):
    def __init__(self, path):
        super().__init__(f"File not found: {path}")
        self.path = path


class NotAPythonFileError(ReviewError):
    def __init__(self, path):
        super().__init__(f"Not a Python file (expected .py): {path}")
        self.path = path


class InvalidPythonSourceError(ReviewError):
    def __init__(self, source_name, line_number):
        super().__init__(
            f"{source_name} is not valid Python "
            f"(syntax error on line {line_number})")
        self.line_number = line_number
