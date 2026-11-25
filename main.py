"""AI Code Reviewer: finds security problems and copy-paste in Python code.

Usage:
    python main.py <file.py>

Exit codes: 0 = no issues, 1 = issues found, 2 = the file could not be read.
"""

import sys

from reviewer.code_reviewer import create_default_reviewer
from reviewer.exceptions import ReviewError
from reviewer.report_formatter import ReportFormatter
from reviewer.source_file import SourceFile

EXIT_NO_ISSUES = 0
EXIT_ISSUES_FOUND = 1
EXIT_ERROR = 2


def main(arguments):
    if len(arguments) != 1:
        print("Usage: python main.py <file.py>")
        return EXIT_ERROR
    try:
        source_file = SourceFile.from_path(arguments[0])
    except ReviewError as error:
        print(f"Error: {error}")
        return EXIT_ERROR

    findings = create_default_reviewer().review(source_file)
    print(ReportFormatter().format(source_file.name, findings))
    return EXIT_ISSUES_FOUND if findings else EXIT_NO_ISSUES


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
