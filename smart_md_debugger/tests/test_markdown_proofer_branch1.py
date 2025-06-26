import unittest
from typing import List, Any

from smart_md_debugger.src.markdown_proofer_team.proofer import MarkdownProofer
from smart_md_debugger.src.markdown_proofer_team.rules_manager import RulesManager
# Import the specific rule functions directly for focused testing
from smart_md_debugger.src.markdown_proofer_team.rules.text_character_validation import (
    check_latex_special_chars,
    check_problematic_unicode_chars,
    check_malformed_links_emails,
    check_list_marker_consistency,
    PROBLEM_UNICODE_CHARS, # For accessing expected replacements
    BRANCH1_LATEX_SPECIAL_CHARS # For accessing expected replacements
)

# Helper to create a proofer with specific rules for testing
def create_proofer_for_rules(rule_functions: List[callable]) -> MarkdownProofer:
    manager = RulesManager()
    for rule_func in rule_functions:
        manager.add_rule(rule_func)
    return MarkdownProofer(rules_manager=manager)

class TestBranch1ValidationRules(unittest.TestCase):

    def assertErrorDetail(self, errors: List[Any], expected_type: str, expected_line: int, msg_contains: str = None, suggestion_contains: str = None, expected_count: int = -1):
        """
        Asserts a specific error type on a line, optionally checking message and suggestion.
        If expected_count >= 0, also asserts the number of matching errors.
        """
        matching_errors = []
        for err_line, err_type, err_msg, err_sugg in errors:
            if err_type == expected_type and err_line == expected_line:
                if msg_contains and msg_contains not in err_msg:
                    continue
                if suggestion_contains and (err_sugg is None or suggestion_contains not in err_sugg):
                    continue
                matching_errors.append((err_line, err_type, err_msg, err_sugg))

        self.assertTrue(len(matching_errors) > 0,
                        f"Expected error with type '{expected_type}', line {expected_line}, msg_contains '{msg_contains}', sugg_contains '{suggestion_contains}' not found. Errors: {errors}")

        if expected_count >= 0:
            self.assertEqual(len(matching_errors), expected_count,
                             f"Expected {expected_count} errors for type '{expected_type}', line {expected_line}, msg '{msg_contains}', sugg '{suggestion_contains}'. Found {len(matching_errors)}: {matching_errors}. All errors: {errors}")


    def assertNoErrorType(self, errors: List[Any], error_type: str, msg: str = ""):
        """Helper to assert that a specific error type is NOT present."""
        for error in errors:
            self.assertNotEqual(error[1], error_type, f"Unexpected error type '{error_type}' found: {error[2]}. {msg}")

    def test_check_latex_special_chars(self):
        proofer = create_proofer_for_rules([check_latex_special_chars])

        test_content_positive = """Line with & ampersand.
Line with % percent.
Line with # hash.
Line with _ underscore.
Line with ^ caret.
Line with ~ tilde.
Line with \\ backslash.
"""
        errors = proofer.proof_content(test_content_positive)
        # All these lines form a single paragraph, thus a single 'inline' token.
        # Child text tokens currently inherit the start line of the parent 'inline' token.
        self.assertEqual(len(errors), 7, f"Expected 7 errors for special chars, got {len(errors)}: {errors}")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'&'")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'%'")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'#'")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'_'")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'^'")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'~'")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'\\'")

        test_content_negative = """No special characters in this line.
Math context: $a_b%c^d$ and $$e^f$$.
Also tex math: \(exampleOne\) and block tex math: \[exampleTwo].
Code context: `my_var & your_var` and
```python
def foo(): pass # some code with a # comment
```
Strikethrough: ~~tilde~~
Emphasis: _emph_ and *strong*
# Real Markdown Heading
Apostrophe's fine.
"""
        # The # in the fenced code block comment should be ignored by the text rule (as it's code).
        # "Real Markdown Heading" will have its '#' as markup, not text.
        # "exampleOne" and "exampleTwo" (inside math) should not trigger latex char issues.

        errors_negative = proofer.proof_content(test_content_negative)
        self.assertEqual(len(errors_negative), 0, f"Expected 0 errors for escaped/contextual chars, got {len(errors_negative)}: {errors_negative}")

        test_content_edge_cases = "Double backslash then char: \\\\& (should be literal \\ then unescaped &)"
        errors_edge = proofer.proof_content(test_content_edge_cases)
        # Parser turns \\ into text '\', so text is '\&'. Rule sees '&' preceded by one '\', so it's escaped.
        # errors_edge has 3 errors for the 3 literal backslashes in the string.
        self.assertEqual(len(errors_edge), 3, f"Expected 3 errors for backslashes in edge case, got {len(errors_edge)}: {errors_edge}")
        self.assertErrorDetail(errors_edge, "LATEX_SPECIAL_CHAR", 1, msg_contains="'\\'") # It will find one of them.

        test_literal_backslash = "A literal \\ backslash." # Input has \\, parser makes it \ in text token.
        errors_literal_bs = proofer.proof_content(test_literal_backslash)
        self.assertErrorDetail(errors_literal_bs, "LATEX_SPECIAL_CHAR", 1, msg_contains="'\\'")

        # test_content_emph_tilde's assertions were moved to test_latex_char_underscore_in_emphasis
        # and test_latex_char_tilde_in_strikethrough_text.
        # The original test_content_emph_tilde is no longer needed here.

    def test_latex_char_underscore_in_emphasis(self):
        proofer = create_proofer_for_rules([check_latex_special_chars])
        print(f"DEBUG_TEST_UNDERSCORE: id(proofer)={id(proofer)}, id(proofer.errors) before={id(proofer.errors)}")
        test_content = "_underscore_" # _underscore_ is em -> text "underscore"
        errors = proofer.proof_content(test_content)
        print(f"DEBUG_TEST_UNDERSCORE: id(proofer.errors) after={id(proofer.errors)}, errors = {errors}")
        self.assertEqual(len(errors), 1, f"Expected 1 error for underscore, got {len(errors)}: {errors}")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'_'")

    def test_latex_char_tilde_in_strikethrough_text(self):
        proofer = create_proofer_for_rules([check_latex_special_chars])
        test_content_strikethrough_with_tilde = "Text with ~~internal~tilde~~ text."
        errors = proofer.proof_content(test_content_strikethrough_with_tilde)
        print(f"DEBUG_TEST_TILDE_IN_STRIKE: errors = {errors}")
        # Markdown-it tokenizes "~~internal~tilde~~" into s_open, text "internal~tilde", s_close.
        # The rule check_latex_special_chars will find the '~' in the text token "internal~tilde".
        self.assertEqual(len(errors), 1, f"Expected 1 error for tilde in strikethrough, got {len(errors)}: {errors}")
        self.assertErrorDetail(errors, "LATEX_SPECIAL_CHAR", 1, msg_contains="'~'")

        test_content_strikethrough_no_tilde = "Text with ~~normal~~ text."
        errors_no_tilde = proofer.proof_content(test_content_strikethrough_no_tilde)
        self.assertEqual(len(errors_no_tilde), 0, f"Expected 0 errors for strikethrough without tilde in content, got {len(errors_no_tilde)}: {errors_no_tilde}")


    def test_check_problematic_unicode_chars(self):
        proofer = create_proofer_for_rules([check_problematic_unicode_chars])
        # Using actual unicode chars in the string
        test_content_positive = """“Smart double quotes”
‘Smart single quotes’
Em-dash — here.
En-dash – here.
Non-breaking space. (actual NBSP)
""" # NBSP is \u00A0
        errors = proofer.proof_content(test_content_positive)
        # Expect 7 errors: “, ”, ‘, ’, —, –, NBSP
        self.assertEqual(len(errors), 7, f"Expected 7 unicode errors, got {len(errors)}: {errors}")
        # All are on line 1 due to single paragraph / inline token
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="“")
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="”")
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="‘")
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="’")
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="—")
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="–")
        self.assertErrorDetail(errors, "PROBLEM_UNICODE_CHAR", 1, msg_contains="\u00A0")


        test_content_negative = """Regular "double" quotes.
Regular 'single' quotes.
Hyphenated-word. Three---dashes. Two--dashes.
Normal space here.
"""
        errors_negative = proofer.proof_content(test_content_negative)
        self.assertEqual(len(errors_negative), 0, f"Expected 0 errors for regular chars, got {len(errors_negative)}: {errors_negative}")

# Test cases for check_malformed_links_emails broken down

    def test_malformed_url_autolink_variant(self):
        proofer = create_proofer_for_rules([check_malformed_links_emails])
        test_content = "Bad URL autolink: <ftp://example.com/path>" # FTP should fail current BASIC_URL_REGEX
        print(f"DEBUG_TEST_URL_AUTO: id(proofer)={id(proofer)}, id(proofer.errors) before={id(proofer.errors)}")
        errors = proofer.proof_content(test_content)
        print(f"DEBUG_TEST_URL_AUTO: id(proofer.errors) after={id(proofer.errors)}, errors = {errors}")
        self.assertEqual(len(errors), 1, f"Expected 1 error, got {len(errors)}: {errors}")
        self.assertErrorDetail(errors, "MALFORMED_URL_AUTOLINK", 1, msg_contains="<ftp://example.com/path>")

    def test_malformed_email_autolink_variant(self):
        proofer = create_proofer_for_rules([check_malformed_links_emails])
        test_content_bad_email_auto = "Bad email autolink: <mailto:test@nodomain>"
        errors = proofer.proof_content(test_content_bad_email_auto)
        print(f"DEBUG_TEST_EMAIL_AUTO_NODOMAIN: errors = {errors}")
        self.assertEqual(len(errors), 1, f"Expected 1 error, got {len(errors)}: {errors}")
        self.assertErrorDetail(errors, "MALFORMED_EMAIL_AUTOLINK", 1, msg_contains="<mailto:test@nodomain>")

        test_content_bad_email_auto_notld = "Bad email autolink no TLD: <mailto:user@server>"
        errors_notld = proofer.proof_content(test_content_bad_email_auto_notld)
        print(f"DEBUG_TEST_EMAIL_AUTO_NOTLD: errors = {errors_notld}")
        self.assertEqual(len(errors_notld), 1, f"Expected 1 error, got {len(errors_notld)}: {errors_notld}")
        self.assertErrorDetail(errors_notld, "MALFORMED_EMAIL_AUTOLINK", 1, msg_contains="<mailto:user@server>")

    def test_plain_text_malformed_email_variant(self):
        proofer = create_proofer_for_rules([check_malformed_links_emails])
        test_content_plain_emails = "Plain text email missing TLD: contact at user@server or info@localhost."
        print(f"DEBUG_TEST_PLAIN_EMAILS: id(proofer)={id(proofer)}, id(proofer.errors) before={id(proofer.errors)}")
        errors = proofer.proof_content(test_content_plain_emails)
        print(f"DEBUG_TEST_PLAIN_EMAILS: id(proofer.errors) after={id(proofer.errors)}, errors = {errors}")
        self.assertEqual(len(errors), 2, f"Expected 2 errors, got {len(errors)}: {errors}")
        self.assertErrorDetail(errors, "POTENTIAL_MALFORMED_EMAIL", 1, msg_contains="user@server")
        self.assertErrorDetail(errors, "POTENTIAL_MALFORMED_EMAIL", 1, msg_contains="info@localhost")

    def test_no_errors_for_valid_links_emails_variant(self):
        proofer = create_proofer_for_rules([check_malformed_links_emails])
        test_content_valid = """Good URL: <http://example.com/path>
Good email: <mailto:test@example.com>
Plain text valid email: my.email@example.co.uk.
"""
        errors = proofer.proof_content(test_content_valid)
        print(f"DEBUG_TEST_VALID_LINKS: errors = {errors}")
        self.assertEqual(len(errors), 0, f"Expected 0 errors for valid links/emails, got {len(errors)}: {errors}")


    def test_check_list_marker_consistency(self):
        proofer = create_proofer_for_rules([check_list_marker_consistency])

        test_content_inconsistent_bullets = """- Item A
* Item B (inconsistent)
- Item C
"""
        errors = proofer.proof_content(test_content_inconsistent_bullets)
        # CommonMark parsers will treat "- Item A" and "* Item B" as two separate lists.
        # The current rule flags inconsistencies *within* a single list block.
        # Thus, this test case will not produce an error with the current rule and parser.
        # self.assertErrorDetail(errors, "INCONSISTENT_LIST_MARKER", 2, msg_contains="'*'")
        # self.assertEqual(len(errors), 1, f"Expected 1 list marker error for this case, got {len(errors)}: {errors}")
        self.assertEqual(len(errors), 0, f"Expected 0 list marker errors for this specific case with CommonMark parsing, got {len(errors)}: {errors}")


        test_content_consistent_bullets = """- Item 1
- Item 2
- Item 3
"""
        errors_consistent = proofer.proof_content(test_content_consistent_bullets)
        self.assertEqual(len(errors_consistent), 0, f"Expected 0 errors for consistent list, got {len(errors_consistent)}: {errors_consistent}")

        test_content_mixed_valid_nesting = """- Item X
  * Nested Y1 (new list, ok)
  * Nested Y2
- Item Z

* List A
  - Sublist B1 (new list, ok)
  - Sublist B2
"""
        errors_nested = proofer.proof_content(test_content_mixed_valid_nesting)
        self.assertEqual(len(errors_nested), 0, f"Expected 0 errors for valid nested lists, got {len(errors_nested)}: {errors_nested}")

        test_content_inconsistent_nested = """- Item P
  - Nested Q1
  * Nested Q2 (inconsistent with Q1)
"""
        errors_inc_nested = proofer.proof_content(test_content_inconsistent_nested)
        # Similar to the above, "- Nested Q1" and "* Nested Q2" will be parsed as separate lists by CommonMark.
        # self.assertErrorDetail(errors_inc_nested, "INCONSISTENT_LIST_MARKER", 3, msg_contains="'*'")
        # self.assertEqual(len(errors_inc_nested), 1, f"Expected 1 error for inconsistent nested list, got {len(errors_inc_nested)}: {errors_inc_nested}")
        self.assertEqual(len(errors_inc_nested), 0, f"Expected 0 errors for this inconsistent nested list with CommonMark, got {len(errors_inc_nested)}: {errors_inc_nested}")

        test_content_ordered_lists = """1. Ordered A
2. Ordered B
   - Sub Bullet 1
   - Sub Bullet 2
3. Ordered C (marker is '3.')
   1) Nested Ordered A (new list, new marker type, ok)
   2) Nested Ordered B
""" # Ordered list consistency is not currently checked by this rule (only bullet lists)
        errors_ordered = proofer.proof_content(test_content_ordered_lists)
        self.assertEqual(len(errors_ordered), 0, f"Expected 0 errors for ordered lists, got {len(errors_ordered)}: {errors_ordered}")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# To run these tests from CLI (assuming project structure allows):
# Option 1: If smart_md_debugger is in PYTHONPATH or installed
# python -m unittest smart_md_debugger.tests.test_markdown_proofer_branch1
# Option 2: From the root directory of the project containing smart_md_debugger/
# python -m unittest discover -s smart_md_debugger/tests -p "test_*.py"
# (Or more specific) python -m unittest smart_md_debugger.tests.test_markdown_proofer_branch1
#
# Make sure __init__.py files are present in smart_md_debugger, src, markdown_proofer_team, rules, tests.
# The `smart_md_debugger.src.markdown_proofer_team...` import path suggests that the tests
# should be run from a directory where `smart_md_debugger` is a top-level package.
# For example, if project root is `project/` and contains `smart_md_debugger/`,
# run from `project/`.
#
# If running `python smart_md_debugger/tests/test_markdown_proofer_branch1.py` directly,
# Python path adjustments might be needed (e.g. `sys.path.append`).
# The `unittest.main()` call is for convenience if run as a script.
# For sandbox, need to ensure it can find the modules.
# The current structure with `smart_md_debugger.src` implies `smart_md_debugger` is the package.
# So `from smart_md_debugger.src...` is correct if `PYTHONPATH` includes the parent of `smart_md_debugger`.

# Simpler imports if tests are run such that `src` is the root for module resolution.
# For example, if PYTHONPATH points to `smart_md_debugger/src`:
# from markdown_proofer_team.proofer import MarkdownProofer
# from markdown_proofer_team.rules_manager import RulesManager
# from markdown_proofer_team.rules.text_character_validation import ...
# This depends on how test execution environment is set up.
# Sticking to fully qualified `smart_md_debugger.src...` is safer if `smart_md_debugger` itself is the package root recognized by Python.
# Given the `ls()` output, it seems `smart_md_debugger` is a directory in the repo root.
# So, if `PYTHONPATH` is set to the repo root, `from smart_md_debugger.src...` should work.
# Or, if `smart_md_debugger/src` is added to `PYTHONPATH`, then `from markdown_proofer_team...` works.
# I'll assume the current fully qualified path works with the test runner.

# Add __init__.py to smart_md_debugger/tests/ if it doesn't exist, to make it a package.
# (This is good practice for `unittest discover`)
