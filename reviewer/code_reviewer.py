"""Combines the detectors and returns one ordered list of findings."""

from reviewer.detectors.duplicate_detector import DuplicateDetector
from reviewer.detectors.security_detector import SecurityDetector


class CodeReviewer:
    def __init__(self, detectors):
        self._detectors = list(detectors)

    def review(self, source_file):
        findings = [finding
                    for detector in self._detectors
                    for finding in detector.find_issues(source_file)]
        return sorted(findings, key=most_serious_first)


def create_default_reviewer():
    return CodeReviewer([SecurityDetector(), DuplicateDetector()])


def most_serious_first(finding):
    return finding.severity.value, finding.line
