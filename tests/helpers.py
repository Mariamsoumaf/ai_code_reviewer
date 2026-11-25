"""Small helpers shared by the tests."""

import textwrap

from reviewer.source_file import SourceFile


def source_from(code):
    return SourceFile(textwrap.dedent(code))
