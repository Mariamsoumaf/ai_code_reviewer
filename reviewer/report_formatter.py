"""Turns a list of findings into a readable text report."""

from reviewer.finding import Severity

SEPARATOR_WIDTH = 60


class ReportFormatter:
    def format(self, source_name, findings):
        lines = [f"AI Code Review: {source_name}", "=" * SEPARATOR_WIDTH]
        lines += [self._format_finding(finding) for finding in findings]
        lines += ["-" * SEPARATOR_WIDTH, self._summary(findings)]
        return "\n".join(lines)

    def _format_finding(self, finding):
        return (f"[{finding.severity.name:<6}] {finding.category:<9} "
                f"line {finding.line:>3}: {finding.message}")

    def _summary(self, findings):
        if not findings:
            return "No issues found ✅"
        counts = [f"{self._count(findings, severity)} {severity.name.lower()}"
                  for severity in Severity]
        return f"Summary: {', '.join(counts)} ({len(findings)} total)"

    def _count(self, findings, severity):
        return sum(1 for finding in findings if finding.severity == severity)
