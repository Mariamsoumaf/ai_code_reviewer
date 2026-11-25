"""Runs every security rule on every part of the code."""

from reviewer.detectors.detector import Detector
from reviewer.detectors.security_rules import all_security_rules


class SecurityDetector(Detector):
    def __init__(self, rules=None):
        self._rules = rules if rules is not None else all_security_rules()

    def find_issues(self, source_file):
        findings = []
        for node in source_file.nodes():
            for rule in self._rules:
                findings.extend(rule.inspect(node))
        return remove_repeats(findings)


def remove_repeats(findings):
    return list(dict.fromkeys(findings))
