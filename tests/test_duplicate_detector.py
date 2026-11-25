import unittest

from reviewer.detectors.duplicate_detector import DuplicateDetector
from tests.helpers import source_from

FIVE_LINE_BLOCK = ("total = 0\n"
                   "count = 0\n"
                   "for price in prices:\n"
                   "    total += price\n"
                   "    count += 1\n")


class DuplicateDetectorTest(unittest.TestCase):
    def setUp(self):
        self.detector = DuplicateDetector()

    def test_finds_block_copied_twice(self):
        code = FIVE_LINE_BLOCK + "print(total)\n" + FIVE_LINE_BLOCK
        findings = self.detector.find_issues(source_from(code))
        self.assertEqual(len(findings), 1)

    def test_reports_line_where_copy_starts(self):
        code = FIVE_LINE_BLOCK + "print(total)\n" + FIVE_LINE_BLOCK
        finding = self.detector.find_issues(source_from(code))[0]
        self.assertEqual(finding.line, 7)

    def test_ignores_blocks_shorter_than_minimum(self):
        short_block = "first = 1\nsecond = 2\nthird = 3\nfourth = 4\n"
        code = short_block + "print(first)\n" + short_block
        self.assertEqual(self.detector.find_issues(source_from(code)), [])

    def test_ignores_blank_lines_and_comments_inside_copy(self):
        changed_copy = FIVE_LINE_BLOCK.replace(
            "count = 0\n", "count = 0\n\n# start the loop\n")
        code = FIVE_LINE_BLOCK + "print(total)\n" + changed_copy
        self.assertEqual(len(self.detector.find_issues(source_from(code))), 1)

    def test_code_without_copies_has_no_findings(self):
        self.assertEqual(
            self.detector.find_issues(source_from(FIVE_LINE_BLOCK)), [])


if __name__ == "__main__":
    unittest.main()
