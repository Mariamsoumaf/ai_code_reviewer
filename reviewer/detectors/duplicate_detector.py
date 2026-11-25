"""Finds blocks of code that were copied and pasted."""

from dataclasses import dataclass

from reviewer.detectors.detector import Detector
from reviewer.finding import Finding, Severity

MIN_DUPLICATE_LINES = 5
COMMENT_PREFIX = "#"


@dataclass(frozen=True)
class CodeLine:
    number: int
    text: str


class DuplicateDetector(Detector):
    def __init__(self, min_lines=MIN_DUPLICATE_LINES):
        self._min_lines = min_lines

    def find_issues(self, source_file):
        code_lines = self._meaningful_lines(source_file)
        first_positions = {}
        findings = []
        position = 0
        while position <= len(code_lines) - self._min_lines:
            block = self._block_at(code_lines, position)
            original = first_positions.setdefault(block, position)
            if self._is_separate_copy(original, position):
                length = self._copy_length(code_lines, original, position)
                findings.append(self._finding(
                    code_lines[original:original + length],
                    code_lines[position:position + length]))
                position += length
            else:
                position += 1
        return findings

    def _meaningful_lines(self, source_file):
        code_lines = []
        for number, text in enumerate(source_file.lines(), start=1):
            stripped = text.strip()
            if stripped and not stripped.startswith(COMMENT_PREFIX):
                code_lines.append(CodeLine(number, stripped))
        return code_lines

    def _block_at(self, code_lines, position):
        block = code_lines[position:position + self._min_lines]
        return tuple(code_line.text for code_line in block)

    def _is_separate_copy(self, original, position):
        return original + self._min_lines <= position

    def _copy_length(self, code_lines, original, position):
        length = self._min_lines
        while (position + length < len(code_lines)
               and original + length < position
               and code_lines[original + length].text
               == code_lines[position + length].text):
            length += 1
        return length

    def _finding(self, original_block, copied_block):
        copy_start = copied_block[0].number
        message = (f"lines {copy_start}-{copied_block[-1].number} repeat "
                   f"lines {original_block[0].number}-"
                   f"{original_block[-1].number}: "
                   "move them into one shared function")
        return Finding("DUPLICATE", Severity.LOW, copy_start, message)
