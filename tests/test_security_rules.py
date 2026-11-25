"""Each rule is tested with unsafe code (must be found) and safe code
(must be ignored)."""

import unittest

from reviewer.detectors.security_detector import SecurityDetector
from reviewer.detectors.security_rules import (CodeExecutionRule,
                                               HardcodedSecretRule,
                                               ShellInjectionRule,
                                               SqlInjectionRule,
                                               UnsafeDeserializationRule,
                                               WeakHashRule)
from reviewer.finding import Severity
from tests.helpers import source_from


def lines_found_by(rule, code):
    findings = SecurityDetector([rule]).find_issues(source_from(code))
    return [finding.line for finding in findings]


class CodeExecutionRuleTest(unittest.TestCase):
    def test_finds_eval(self):
        self.assertEqual(lines_found_by(CodeExecutionRule(), "eval(text)"),
                         [1])

    def test_finds_exec(self):
        self.assertEqual(lines_found_by(CodeExecutionRule(), "exec(text)"),
                         [1])

    def test_ignores_safe_conversion(self):
        self.assertEqual(lines_found_by(CodeExecutionRule(), "float(text)"),
                         [])


class HardcodedSecretRuleTest(unittest.TestCase):
    def test_finds_password_in_variable(self):
        code = 'DB_PASSWORD = "admin123"'
        self.assertEqual(lines_found_by(HardcodedSecretRule(), code), [1])

    def test_finds_api_key_in_keyword_argument(self):
        code = 'connect(api_key="sk-12345")'
        self.assertEqual(lines_found_by(HardcodedSecretRule(), code), [1])

    def test_ignores_secret_read_from_environment(self):
        code = 'DB_PASSWORD = os.environ["DB_PASSWORD"]'
        self.assertEqual(lines_found_by(HardcodedSecretRule(), code), [])

    def test_ignores_normal_text(self):
        code = 'title = "Welcome"'
        self.assertEqual(lines_found_by(HardcodedSecretRule(), code), [])


class SqlInjectionRuleTest(unittest.TestCase):
    def test_finds_concatenated_query(self):
        code = 'query = "SELECT * FROM users WHERE name = " + name'
        self.assertEqual(lines_found_by(SqlInjectionRule(), code), [1])

    def test_finds_f_string_query(self):
        code = 'run(f"DELETE FROM users WHERE id = {user_id}")'
        self.assertEqual(lines_found_by(SqlInjectionRule(), code), [1])

    def test_finds_format_query(self):
        code = 'run("UPDATE users SET name = {}".format(name))'
        self.assertEqual(lines_found_by(SqlInjectionRule(), code), [1])

    def test_ignores_parameterized_query(self):
        code = 'run("SELECT * FROM users WHERE name = ?", (name,))'
        self.assertEqual(lines_found_by(SqlInjectionRule(), code), [])

    def test_ignores_text_that_is_not_sql(self):
        code = 'greeting = "Hello " + name'
        self.assertEqual(lines_found_by(SqlInjectionRule(), code), [])


class ShellInjectionRuleTest(unittest.TestCase):
    def test_finds_shell_true(self):
        code = 'subprocess.run("ls " + folder, shell=True)'
        self.assertEqual(lines_found_by(ShellInjectionRule(), code), [1])

    def test_finds_os_system(self):
        code = 'os.system("rm " + name)'
        self.assertEqual(lines_found_by(ShellInjectionRule(), code), [1])

    def test_ignores_argument_list(self):
        code = 'subprocess.run(["ls", folder])'
        self.assertEqual(lines_found_by(ShellInjectionRule(), code), [])


class UnsafeDeserializationRuleTest(unittest.TestCase):
    def test_finds_pickle_load_with_medium_severity(self):
        source_file = source_from("data = pickle.load(file)")
        rule = UnsafeDeserializationRule()
        findings = SecurityDetector([rule]).find_issues(source_file)
        self.assertEqual(findings[0].severity, Severity.MEDIUM)

    def test_ignores_json_load(self):
        code = "data = json.load(file)"
        self.assertEqual(
            lines_found_by(UnsafeDeserializationRule(), code), [])


class WeakHashRuleTest(unittest.TestCase):
    def test_finds_md5_hash(self):
        code = "digest = hashlib.md5(text).hexdigest()"
        self.assertEqual(lines_found_by(WeakHashRule(), code), [1])

    def test_ignores_pbkdf2_hash(self):
        code = 'digest = hashlib.pbkdf2_hmac("sha256", text, salt, 1000)'
        self.assertEqual(lines_found_by(WeakHashRule(), code), [])


class SecurityDetectorTest(unittest.TestCase):
    def test_reports_one_finding_for_a_long_concatenation(self):
        code = 'query = "SELECT * FROM t WHERE a = " + first + " AND " + last'
        self.assertEqual(lines_found_by(SqlInjectionRule(), code), [1])


if __name__ == "__main__":
    unittest.main()
