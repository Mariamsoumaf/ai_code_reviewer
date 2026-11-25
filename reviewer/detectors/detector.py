"""The abstraction every detector follows."""

from abc import ABC, abstractmethod


class Detector(ABC):
    @abstractmethod
    def find_issues(self, source_file):
        """Return a list of Findings (an empty list when the code is fine)."""
