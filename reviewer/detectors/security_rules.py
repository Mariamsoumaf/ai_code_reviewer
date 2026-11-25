"""Security rules. Each rule is a small class with one responsibility.

To support a new kind of vulnerability, add a new SecurityRule subclass;
no existing class has to change (Open/Closed Principle).
"""

import ast
import re
from abc import ABC, abstractmethod

from reviewer.finding import Finding, Severity

CATEGORY = "SECURITY"
SECRET_NAME_PATTERN = re.compile(
    r"(password|passwd|pwd|secret|api_?key|token)", re.IGNORECASE)
SQL_KEYWORDS = ("SELECT", "INSERT", "UPDATE", "DELETE", "DROP")


class SecurityRule(ABC):
    severity = Severity.HIGH

    def inspect(self, node):
        if self.matches(node):
            return [Finding(CATEGORY, self.severity, node.lineno,
                            self.describe(node))]
        return []

    @abstractmethod
    def matches(self, node):
        """Return True when the node breaks this rule."""

    @abstractmethod
    def describe(self, node):
        """Explain the problem and the safer alternative."""


class ForbiddenCallRule(SecurityRule):
    """A rule that only checks the name of the called function."""
    forbidden_calls = set()

    def matches(self, node):
        return (isinstance(node, ast.Call)
                and dotted_name(node.func) in self.forbidden_calls)


class CodeExecutionRule(ForbiddenCallRule):
    forbidden_calls = {"eval", "exec"}

    def describe(self, node):
        return (f"{dotted_name(node.func)}() runs any code it receives: "
                "parse the input explicitly instead")


class HardcodedSecretRule(SecurityRule):
    def matches(self, node):
        if isinstance(node, ast.Assign):
            return any(self._is_secret(target, node.value)
                       for target in node.targets)
        if isinstance(node, ast.keyword):
            return self._is_secret_name(node.arg) and is_text(node.value)
        return False

    def describe(self, node):
        return ("secret written inside the code: "
                "load it from an environment variable")

    def _is_secret(self, target, assigned_value):
        return (self._is_secret_name(dotted_name(target))
                and is_text(assigned_value))

    def _is_secret_name(self, name):
        return bool(name) and bool(SECRET_NAME_PATTERN.search(name))


class SqlInjectionRule(SecurityRule):
    def matches(self, node):
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            return self._mixes_sql_with_variables(node)
        return self._is_formatted_sql_call(node)

    def describe(self, node):
        return ("SQL query built from strings (SQL injection): "
                "use a parameterized query with ? placeholders")

    def _mixes_sql_with_variables(self, node):
        parts = list(ast.walk(node))
        has_sql_text = any(starts_with_sql(part) for part in parts)
        has_variable = any(isinstance(part, (ast.Name, ast.Attribute,
                                             ast.Call, ast.FormattedValue))
                           for part in parts)
        return has_sql_text and has_variable

    def _is_formatted_sql_call(self, node):
        return (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "format"
                and starts_with_sql(node.func.value))


class ShellInjectionRule(SecurityRule):
    def matches(self, node):
        if not isinstance(node, ast.Call):
            return False
        return dotted_name(node.func) == "os.system" or self._uses_shell(node)

    def describe(self, node):
        return ("command runs through the shell (command injection): "
                "pass a list of arguments without shell=True")

    def _uses_shell(self, call):
        return any(keyword.arg == "shell" and is_true(keyword.value)
                   for keyword in call.keywords)


class UnsafeDeserializationRule(ForbiddenCallRule):
    severity = Severity.MEDIUM
    forbidden_calls = {"pickle.load", "pickle.loads", "marshal.loads"}

    def describe(self, node):
        return (f"{dotted_name(node.func)}() can run hidden code from the "
                "data: use json for untrusted data")


class WeakHashRule(ForbiddenCallRule):
    severity = Severity.MEDIUM
    forbidden_calls = {"hashlib.md5", "hashlib.sha1"}

    def describe(self, node):
        return (f"{dotted_name(node.func)} is too weak for passwords: "
                "use hashlib.pbkdf2_hmac with a salt")


def all_security_rules():
    return [CodeExecutionRule(), HardcodedSecretRule(), SqlInjectionRule(),
            ShellInjectionRule(), UnsafeDeserializationRule(),
            WeakHashRule()]


def dotted_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = dotted_name(node.value)
        return f"{owner}.{node.attr}" if owner else node.attr
    return ""


def is_text(node):
    return (isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value != "")


def is_true(node):
    return isinstance(node, ast.Constant) and node.value is True


def starts_with_sql(node):
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return False
    return node.value.strip().upper().startswith(SQL_KEYWORDS)
