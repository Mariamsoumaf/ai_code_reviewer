import unittest
from pathlib import Path

from reviewer.code_reviewer import CodeReviewer, create_default_reviewer
from reviewer.detectors.detector import Detector
from reviewer.finding import Finding, Severity
from reviewer.report_formatter import ReportFormatter
from reviewer.source_file import SourceFile
from tests.helpers import source_from

EXAMPLES_FOLDER = Path(__file__).parent.parent / "examples"


class FixedFindingsDetector(Detector):
    """A fake detector, so the reviewer can be tested on its own."""

    def __init__(self, findings):
        self._findings = findings

    def find_issues(self, source_file):
        return self._findings


class CodeReviewerTest(unittest.TestCase):
    def test_puts_most_serious_findings_first(self):
        low = Finding("DUPLICATE", Severity.LOW, 1, "copy")
        high = Finding("SECURITY", Severity.HIGH, 9, "eval")
        reviewer = CodeReviewer([FixedFindingsDetector([low]),
                                 FixedFindingsDetector([high])])
        findings = reviewer.review(source_from("answer = 42"))
        self.assertEqual(findings, [high, low])

    def test_unsafe_example_has_expected_number_of_findings(self):
        source_file = SourceFile.from_path(
            EXAMPLES_FOLDER / "ai_generated_login.py")
        findings = create_default_reviewer().review(source_file)
        self.assertEqual(len(findings), 10)

    def test_fixed_example_has_no_findings(self):
        source_file = SourceFile.from_path(EXAMPLES_FOLDER / "safe_login.py")
        self.assertEqual(create_default_reviewer().review(source_file), [])


class ReportFormatterTest(unittest.TestCase):
    def test_summary_counts_each_severity(self):
        findings = [Finding("SECURITY", Severity.HIGH, 1, "eval"),
                    Finding("SECURITY", Severity.HIGH, 2, "exec"),
                    Finding("DUPLICATE", Severity.LOW, 5, "copy")]
        report = ReportFormatter().format("demo.py", findings)
        self.assertIn("Summary: 2 high, 0 medium, 1 low (3 total)", report)

    def test_clean_report_says_no_issues(self):
        report = ReportFormatter().format("demo.py", [])
        self.assertIn("No issues found", report)


if __name__ == "__main__":
    unittest.main()
