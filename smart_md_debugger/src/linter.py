import re
from typing import List, Tuple, Dict, Any

# Define a structure for linter errors, e.g., a dictionary or a simple class
# For now, a tuple: (line_number: int, error_type: str, message: str, suggestion: str | None)
LinterError = Tuple[int, str, str, str | None]

def report_linter_error(line_number: int, error_type: str, message: str, suggestion: str | None = None) -> LinterError:
    """Helper to create a standardized linter error tuple."""
    return (line_number, error_type, message, suggestion)

class MarkdownLinter:
    def __init__(self, content: str):
        self.content = content
        self.lines = content.splitlines(keepends=True)
        self.errors: List[LinterError] = []

    def get_line_content(self, line_number: int) -> str:
        """Returns the content of a 1-indexed line number."""
        if 1 <= line_number <= len(self.lines):
            return self.lines[line_number - 1]
        return ""

    def add_error(self, line_number: int, error_type: str, message: str, suggestion: str | None = None):
        """Adds an error to the list of found errors."""
        self.errors.append(report_linter_error(line_number, error_type, message, suggestion))

    def run_checks(self):
        """
        Runs all implemented linting checks.
        Subclasses or specific check methods will populate self.errors.
        This base method will be expanded by other methods for each check.
        """
        self._check_backtick_escaping()
        self._check_math_delimiters()
        self._check_environment_delimiters()
        self._check_common_latex_command_issues()
        # ...

    def _check_common_latex_command_issues(self):
        """
        Checks for common issues with LaTeX commands, such as:
        - Double subscripts/superscripts (e.g., x_a_b, x^a^b)
        - Fractions needing braces (e.g., \\frac ab)
        - Common commands needing braces for multi-token arguments (e.g., \\sqrt item)
        """
        # Regex for double subscripts: x_a_b or x_{ab}_c or x_a_{bc}
        # We are looking for script_char -> non-brace basic_arg -> script_char
        # A "basic_arg" is a single character or a command like \alpha.
        # A "braced_arg" is {...}.
        # Pattern: (_{basic_arg}|_{braced_arg}|\^{basic_arg}|\^{braced_arg}) (_{basic_arg}|\^{basic_arg})
        # This is complex. A simpler approach: find x_._. or x^.^.
        # (?<!\{) means "not preceded by { " (to avoid matching _{a_b})
        # (?! ) means "not followed by }" (to avoid matching {a_b}_c)
        # This still doesn't quite capture it easily.

        # Simpler regex for direct double subscripts/superscripts:
        # Looks for X_Y_Z or X^Y^Z or X_Y^Z or X^Y_Z where Y is a single char or simple command
        # and not inside braces already.
        # This needs to be context-aware of math mode, but the linter is not fully context-aware.
        # We'll find the pattern and suggest user review.

        # Double Subscript: Matches a char/group, then `_` + single char/cmd (not `{`), then `_` + char/cmd
        # Example: `a_b_c`, `\alpha_x_y`
        # To avoid false positives like `a_{b_c}` or `a_b_{c_d}` we need to be careful.
        # Let's find `_` followed by a non-brace char/cmd, then another `_`.
        # `([a-zA-Z0-9\\]|\\[a-zA-Z]+)` : a character, number, or \cmd
        # `(?<!{)` : not preceded by {
        # `(?!})` : not followed by }

        # Simplified pattern: find `identifier _ singleToken _ anything` or `identifier ^ singleToken ^ anything`
        # Where singleToken is not starting with {
        double_script_pattern = re.compile(r"""
            (?:[a-zA-Z0-9\\]|\\[a-zA-Z@]+)\s* # Base for the script
            (?:
                (?:_{ ([^}{1}]|\\[a-zA-Z@]+) } \s* _{ ([^}{1}]|\\[a-zA-Z@]+) }) # _{s1}_s2 (s1,s2 single or \cmd) - this is for _{s1}_{s2} which is fine.
              | (?:_{ ([^}{1}]|\\[a-zA-Z@]+) } \s* \^{ ([^}{1}]|\\[a-zA-Z@]+) }) # _{s1}^s2
              | (?: \^{ ([^}{1}]|\\[a-zA-Z@]+) } \s* _{ ([^}{1}]|\\[a-zA-Z@]+) }) # ^{s1}_s2
              | (?: \^{ ([^}{1}]|\\[a-zA-Z@]+) } \s* \^{ ([^}{1}]|\\[a-zA-Z@]+) }) # ^{s1}^s2
                 # The above is for when scripts ARE braced. We want when they are NOT.

              | (?: _ ([^}\s{]) \s* _ )      # x_a_b where a is single char not { or } or space
              | (?: \^ ([^}\s{]) \s* \^ )    # x^a^b
              | (?: _ ([^}\s{]) \s* \^ )      # x_a^b (less common as error, often valid like M_a^b)
              | (?: \^ ([^}\s{]) \s* _ )      # x^a_b (less common as error)
            )
        """, re.VERBOSE)
        # This regex is becoming very complex and prone to false positives/negatives.
        # A simpler, more direct approach for common "illegal double script" might be:
        # Look for `_` or `^` followed by a non-braced argument, immediately followed by another `_` or `^`.
        # Non-braced argument: a single character, or a command like `\alpha`.
        # Pattern: `([_^])([a-zA-Z0-9]|\\[a-zA-Z@]+)\1` -> e.g. `_a_` or `^b^` (this is too simple, means `_a_b`)
        # Pattern: `([_^])([a-zA-Z0-9]|\\[a-zA-Z@]+)\s*([_^])`

        # Let's target the error "Double superscript" or "Double subscript".
        # This typically occurs like `x^1^2` or `x_1_2`.
        # Regex: `([a-zA-Z0-9]|\\[a-zA-Z@]+)\s*([_^])\s*([^{}\s\\]|\\[a-zA-Z@]+)\s*\2`
        #  (base) (script_char1) (non_braced_arg1) (script_char1_again_immediately_or_after_non_braced_arg1)
        # This is hard to get right without full parsing.
        # Alternative: find `x_a_b` or `x^a^b` more directly.
        # `\w+(_[^_\s{^](?![^{]))+` -> this is for multiple subscripts like a_b_c_d
        # A base followed by script char, then a token not starting with '{', then the same script char again.
        # `(?:[a-zA-Z0-9]|\\[a-zA-Z@]+)` : call this 'base_item'
        # `(?:base_item)(?:(?:(_)|(\^))([^{]))+\1` : This is not quite right.

        # Simpler approach for double scripts:
        # Look for script char, then a non-braced item, then THE SAME script char again.
        # e.g. X_A_B (A is not braced) or X^A^B (A is not braced)
        # Pattern: `([a-zA-Z0-9]|\\[a-zA-Z@]+)\s*([_^])\s*(?![{])\s*([a-zA-Z0-9]|\\[a-zA-Z@]+)\s*\2`
        # This means: base item, script char (capture as \2), (negative lookahead for no '{'), another base item, then script char \2 again.

        for line_num, line_content in enumerate(self.lines, 1):
            # Check for double superscripts: e.g., x^a^b or \alpha^1^2
            # Matches: (something ending alphanumeric or a command like \beta) then ^ then (single char or \cmd not starting with {) then ^
            # We look for base^arg1^arg2 where arg1 is not braced.
            # `(?<=[a-zA-Z0-9\}])` : lookbehind for alphanumeric or closing brace (e.g. from x^{ab}^c)
            # `\^([^{])` : caret followed by a non-brace char (arg1)
            # `\^` : then another caret
            # This is still tricky due to lookarounds and context.

            # Simplest direct pattern for x^a^b or x_a_b (where 'a' is a single char not '{')
            # (?:[a-zA-Z0-9\}]) means ends with alphanumeric or }
            # \s* avoids issues with spaces like x ^ a ^ b
            # ([_^]) captures the script char (_ or ^)
            # (?![{]) ensures the first argument is not braced
            # \S+ matches the first argument (one or more non-space chars)
            # \s* then the same script char \1
            # This is trying to find scriptchar ARG1 scriptchar
            # A simpler visual pattern is `[^_^]{character_or_command}[^_^]{non_braced_argument}[^_^]`

            # Focusing on the direct error: `X^A^B` or `X_A_B` where A is simple
            # `\w` (alphanumeric) or `\\command` can be `X` or `A`
            base = r"(?:\w|\\[a-zA-Z@]+[a-zA-Z0-9@]*\*?)" # Word, number, or \command
            simple_arg = r"[^{}\s\\]" # Single char not brace, space, or backslash (could be improved)
                                     # or a command: `| \\ [a-zA-Z@]+`
            simple_arg_or_cmd = r"(?:[^{}\s\\]|\\[a-zA-Z@]+[a-zA-Z0-9@]*\*?)"

            # Pattern: base script_char simple_arg_or_cmd script_char
            # We want to detect if script_char is repeated for the *same base* effectively.
            # e.g. `a^b^c` or `a_b_c`
            # `(pattern_for_X) (script_char_1) (pattern_for_A_non_braced) (script_char_2, must be same as _1 if error)`
            # This is more like: `X script_1 A script_2 B`. If script_1 and script_2 are same and A is not braced, it's an error.

            # Find script char, then a non-braced arg, then the *same* script char again
            # `([_^])` captures the script character. `\1` refers to it.
            # `(?![{])` ensures the argument doesn't start with `{`.
            # `(?:[a-zA-Z0-9]|\\[a-zA-Z@]+)` is a common pattern for a LaTeX token.
            double_script_rx = re.compile(r"([_^])\s*(?![{])\s*(?:[a-zA-Z0-9]|\\[a-zA-Z@]+[a-zA-Z0-9@]*\*?)\s*\1")
            for match in double_script_rx.finditer(line_content):
                script_char = match.group(1)
                type_char = "superscript" if script_char == "^" else "subscript"
                self.add_error(line_num, f"DOUBLE_{type_char.upper()}",
                               f"Potential double {type_char} found: '{match.group(0)}'. LaTeX does not allow consecutive non-braced {type_char}s.",
                               "Use braces for clarity if multiple scripts are intended, e.g., x_{a_b} or x^{a^b}, or x^{ab}_{cd}. If it's x_a_b, it should be x_{ab} or similar.")

            # Check for \frac without braces for multi-character num/den
            # \frac followed by non-braced single char, then non-braced single char is OK: \frac ab
            # \frac followed by non-braced multi-char is usually an error: \frac abc (means \frac{a}{b}c)
            # We look for `\frac` then a non-whitespace char (not `{`), then another non-whitespace char (not `{`).
            # This suggests `\frac XY` where X and Y are single tokens. If X or Y are multi-char, it's suspicious.
            # `\frac\s+([^{}\s])\s*([^{}\s])` -> \frac A B (A,B single chars) - This is OK.
            # `\frac\s+([^{}\s]\S+)\s*([^{}\s]\S*)` -> \frac LongA LongB (problematic)
            # Let's find `\frac` followed by something not starting with `{` and containing more than one char (or a command)
            # Or `\frac{A}B` where B is multi-char and not braced.

            # Pattern: \frac followed by ( (non-braced non-single-char) OR {braced} (non-braced non-single-char) )
            # This is for `\frac longA B` or `\frac A longB` or `\frac longA longB` or `\frac {A} longB` etc.
            # A "single simple token" is one char `[a-zA-Z0-9]` or one command `\cmd`.
            # A "long token" is multiple chars `[a-zA-Z0-9]{2,}` or with scripts `\cmd_b` etc.

            # For \frac: find \frac followed by two arguments. If either argument is not
            # a single character (and not braced) or a simple command (and not braced), flag it.
            # Argument regex: (\\[a-zA-Z@]+[a-zA-Z0-9@]*\*?|[a-zA-Z0-9]) -> single token
            # Argument regex for multi-char: (\S+) -> too general

            # Simpler: \frac followed by space(s), then a char that's not '{', then a char that's not '{'.
            # This is too simple (\frac ab is fine).
            # We care if the "implicit" arguments are longer than one token.
            # `\frac\s+([^\s{].*?[^\s}])\s+([^\s{].*?[^\s}])` - attempts to find two space-separated non-braced args
            # This is hard to make robust.
            # A common error is `\frac 12` (meaning `\frac{1}{2}`) or `\frac \alpha\beta` (meaning `\frac{\alpha}{\beta}`)

            # Focus on commands known to need braces for multi-token args
            commands_needing_braces = ["sqrt", "textbf", "textit", "texttt", "mathbf", "emph"]
            # Pattern: \\(cmd)\s+(?![{])(\\[a-zA-Z@]+[a-zA-Z0-9@]*\*?|\S{2,}|\S+[_^]\S+)
            # (cmd) then space, not followed by {, then (a \cmd OR string of 2+ chars OR string with _ or ^)
            for cmd in commands_needing_braces:
                # Argument is either a LaTeX command, or a non-whitespace token of length > 1,
                # or a token containing _ or ^ (suggesting complex structure).
                # (?![{]) ensures it's not already braced.
                # (\S+) captures the argument. We then check its length or if it's a command.
                # `(?:\s*(\\[a-zA-Z@]+[a-zA-Z0-9@]*\*?|[^{\s](?:[^}\s]*[^}\s])?))`
                # An argument that is not braced and is more than a single character (unless it's a command like \alpha)
                # `\s+(?![{])` : space, then not a brace
                # `( (?: \\[a-zA-Z@]+[a-zA-Z0-9@]*\*? ) | (?: [a-zA-Z0-9]{2,} ) | (?: [a-zA-Z0-9][_^][a-zA-Z0-9] ) )`
                #  ( \cmd ) OR ( aa ) OR ( a_b or a^b )
                # This regex looks for \cmd followed by an unbraced argument that's either a command,
                # or alphanumeric of length 2+, or contains a subscript/superscript.
                arg_pattern = r"(\\(?:[a-zA-Z@]+[a-zA-Z0-9@]*\*?)|[a-zA-Z0-9]{2,}|[a-zA-Z0-9]+(?:[_^][a-zA-Z0-9]+)+)"
                pattern = r"\\" + cmd + r"\s+(?![{])(" + arg_pattern + r")"

                for match in re.finditer(pattern, line_content):
                    argument = match.group(1)
                    self.add_error(line_num, "MISSING_BRACES_ARG",
                                   f"Command \\{cmd} found with potentially unbraced multi-token argument: '{argument}'.",
                                   f"Consider adding braces: \\{cmd}{{{argument}}}.")


    def _check_environment_delimiters(self):
        """
        Checks for mismatched or unclosed LaTeX environment delimiters
        (\\begin{environment} and \\end{environment}).
        Uses a stack-based approach.
        """
        # Regex to find \begin{env} or \end{env}
        # It captures the 'begin' or 'end' part, and the environment name.
        env_regex = re.compile(r"""
            \\(begin|end)\s*\{([a-zA-Z0-9\*]+)\}
        """, re.VERBOSE)

        # Stack stores tuples: (environment_name: str, line_number: int, col_number: int, begin_or_end: str)
        stack: List[Tuple[str, int, int, str]] = []

        for line_num, line_content in enumerate(self.lines, 1):
            for match in env_regex.finditer(line_content):
                begin_or_end = match.group(1) # "begin" or "end"
                env_name = match.group(2)     # e.g., "align", "itemize"
                col_num = match.start()

                if begin_or_end == "begin":
                    stack.append((env_name, line_num, col_num, "begin"))
                elif begin_or_end == "end":
                    if not stack:
                        self.add_error(
                            line_num, "UNMATCHED_END_ENV",
                            f"Unmatched \\end{{{env_name}}} found at line {line_num}, col {col_num}.",
                            "Check for a missing corresponding \\begin statement."
                        )
                    elif stack[-1][0] == env_name: # Correct environment name
                        stack.pop()
                    else: # Mismatched environment name
                        expected_env_name = stack[-1][0]
                        opened_at_line = stack[-1][1]
                        opened_at_col = stack[-1][2]
                        self.add_error(
                            line_num, "MISMATCHED_END_ENV",
                            f"Mismatched \\end{{{env_name}}} at line {line_num}, col {col_num}. "
                            f"Expected \\end{{{expected_env_name}}} to close environment opened at line {opened_at_line}, col {opened_at_col}.",
                            f"Correct the environment name in \\end or the corresponding \\begin."
                        )
                        # Attempt recovery: pop the stack anyway to find further errors.
                        # This assumes the user intended to close *something*.
                        stack.pop()

        # After checking all lines, any remaining items on stack are unclosed environments
        for env_name, line_num, col_num, _ in stack:
            self.add_error(
                line_num, "UNCLOSED_ENV",
                f"Unclosed environment \\begin{{{env_name}}} opened at line {line_num}, col {col_num}.",
                f"Ensure it is properly closed with \\end{{{env_name}}}."
            )

    def _check_math_delimiters(self):
        """
        Checks for mismatched or unclosed math delimiters:
        $, $$, \\\\(, \\\\), \\\\\[, \\\\\]
        Uses a stack-based approach.
        Also flags suspicious mixing like $ ... \\\\).
        """
        # Delimiter types:
        # 'dollar_inline': $
        # 'dollar_display': $$
        # 'paren_inline': \( \)
        # 'bracket_display': \[ \]

        # Regex to find any of our target delimiters, also capturing their type and line context.
        # We need to handle escaping, e.g., `\$` should not be treated as a delimiter.
        # The regex should find non-escaped delimiters.
        # (?<!\\) - negative lookbehind for no preceding backslash.
        delimiter_regex = re.compile(r"""
            (?<!\\)\$\$      # $$ (display)
          | (?<!\\)\$        # $ (inline/display toggle)
          | (?<!\\)\\\(      # \( (inline)
          | (?<!\\)\\\)      # \) (inline)
          | (?<!\\)\\\[      # \[ (display)
          | (?<!\\)\\\]      # \] (display)
        """, re.VERBOSE)

        # Stack stores tuples: (delimiter_string, line_number, column_number, delimiter_type)
        stack: List[Tuple[str, int, int, str]] = []

        # Define opening and closing pairs and their types
        openers = {
            "$": "dollar_toggle", # Special handling for $ as it's a toggle
            "$$": "dollar_display",
            "\\(": "paren_inline",
            "\\[": "bracket_display"
        }
        closers = {
            # "$" is also its own closer for 'dollar_toggle'
            "$$": "dollar_display",
            "\\)": "paren_inline",
            "\\]": "bracket_display"
        }
        # Map closer to its corresponding opener type for validation
        closer_to_opener_type = {
            "$$": "dollar_display",
            "\\)": "paren_inline",
            "\\]": "bracket_display"
            # $ is special
        }

        for line_num, line_content in enumerate(self.lines, 1):
            for match in delimiter_regex.finditer(line_content):
                token = match.group(0)
                col_num = match.start()

                if token == "$": # Toggle case
                    if stack and stack[-1][3] == "dollar_toggle": # Closing an existing $
                        stack.pop()
                    else: # Opening a new $
                        stack.append((token, line_num, col_num, "dollar_toggle"))
                elif token == "$$": # Handle $$ as a toggle similar to $
                    if stack and stack[-1][3] == "dollar_display": # Closing an existing $$
                        stack.pop()
                    else: # Opening a new $$
                        # No mixing check needed here as $$ is display and other common inlines shouldn't be directly inside it without nesting logic
                        stack.append((token, line_num, col_num, "dollar_display"))
                elif token in openers: # For \( and \[
                    # Check for suspicious mixing, e.g. $ ... \( or \( ... $
                    if stack: # Removed token != "$$" as $$ is handled above
                        # If stack top is $ and current opener is \( or \[
                        if stack[-1][3] == "dollar_toggle" and openers[token] in ["paren_inline", "bracket_display"]:
                            self.add_error(
                                line_num, "MIXED_DELIMITERS",
                                f"Suspicious opening of '{token}' at line {line_num}, col {col_num} "
                                f"while an unclosed '{stack[-1][0]}' (opened at line {stack[-1][1]}, col {stack[-1][2]}) is active.",
                                "Ensure math delimiters are consistently paired (e.g., $...$ or \\(...\\))."
                            )
                        # If stack top is \( or \[ and current opener is $
                        elif stack[-1][3] in ["paren_inline", "bracket_display"] and openers[token] == "dollar_toggle":
                             self.add_error(
                                line_num, "MIXED_DELIMITERS",
                                f"Suspicious opening of '{token}' at line {line_num}, col {col_num} "
                                f"while an unclosed '{stack[-1][0]}' (opened at line {stack[-1][1]}, col {stack[-1][2]}) is active.",
                                "Ensure math delimiters are consistently paired."
                            )
                    stack.append((token, line_num, col_num, openers[token]))
                elif token in closers:
                    if not stack:
                        self.add_error(
                            line_num, "UNMATCHED_CLOSER",
                            f"Unmatched closing delimiter '{token}' found at line {line_num}, col {col_num}.",
                            f"Check for a missing opening delimiter like '{ {v: k for k, v in openers.items() if v == closers[token]}[closers[token]] }' or ensure pairs are correct."
                        )
                    elif stack[-1][3] == closers[token]: # Correct closer for the type
                        stack.pop()
                    else: # Mismatched closer
                        expected_opener_char_for_stack_top = stack[-1][0]
                        # Try to find the char for the expected closer
                        expected_closer_char = "unknown"
                        for closer_char, opener_type_val in closer_to_opener_type.items():
                            if opener_type_val == stack[-1][3]:
                                expected_closer_char = closer_char
                                break
                        if stack[-1][3] == "dollar_toggle": expected_closer_char = "$"


                        self.add_error(
                            line_num, "MISMATCHED_CLOSER",
                            f"Mismatched closing delimiter '{token}' at line {line_num}, col {col_num}. "
                            f"Expected a closer for '{expected_opener_char_for_stack_top}' (opened at line {stack[-1][1]}, col {stack[-1][2]}), "
                            f"such as '{expected_closer_char}'.",
                            f"Correct the delimiter or the corresponding opener."
                        )
                        # Potentially pop to recover and find more errors, or stop?
                        # For now, we'll pop to allow further detection, assuming user error.
                        stack.pop()

        # After checking all lines, any remaining items on stack are unclosed
        for token, line_num, col_num, type_val in stack:
            expected_closer = "unknown"
            if type_val == "dollar_toggle": expected_closer = "$"
            else:
                for closer_char, opener_type_val in closer_to_opener_type.items():
                    if opener_type_val == type_val:
                        expected_closer = closer_char
                        break
            self.add_error(
                line_num, "UNCLOSED_DELIMITER",
                f"Unclosed math delimiter '{token}' (type: {type_val}) opened at line {line_num}, col {col_num}.",
                f"Ensure it is properly closed, e.g., with a '{expected_closer}'."
            )


    def _check_backtick_escaping(self):
        """
        Detects common LaTeX commands and environments incorrectly escaped with backticks.
        This addresses the pattern where `\\command` is written as `` `\\command` ``.
        """
        # Regex: finds a single backtick, followed by a literal backslash,
        # then a sequence matching common LaTeX command structures or symbols,
        # followed by any other non-backtick characters (like subscripts or arguments),
        # and finally a closing single backtick.

        # Simpler Regex: A backtick, then a captured group (backslash followed by one or more non-backtick chars), then a backtick.
        # This captures the entire `\foo...` content within the backticks.
        pattern = r"`(\\[^`]+)`"

        # Breaking down the old complex LaTeX part (for reference, not used in the simpler pattern):
        # \\(?:                                 # Non-capturing group for \
        #   [a-zA-Z@]+(?:[a-zA-Z0-9@]*\*?)?    # \command, \command*, \command1, \@command
        #   |                                   # OR
        #   [#$%&~_^<>\\]                       # Single character symbols like \$, \%, \&, \_, \^, \\
        #   |                                   # OR
        #   [bB]egin\{[^{}]*\}                  # \begin{env} or \Begin{env}
        #   |                                   # OR
        #   [eE]nd\{[^{}]*\}                    # \end{env} or \End{env}
        # )[^`]*                                # Followed by any other non-backtick characters (e.g. _L(z) or _{v...})
                                                # This makes sure we capture the full intended LaTeX snippet inside the backticks.

        for line_num, line_content in enumerate(self.lines, 1):
            for match in re.finditer(pattern, line_content):
                improperly_escaped_block = match.group(0)  # The full `` `\foo` ``
                latex_content = match.group(1)            # The `\foo...` part (including the initial \)

                self.add_error(
                    line_num,
                    "BACKTICK_ESCAPING",
                    f"LaTeX-like expression '{latex_content}' found wrapped in single backticks: '{improperly_escaped_block}'. "
                    "This will be treated as literal code.",
                    f"If '{latex_content}' is intended as LaTeX, remove the backticks. "
                    f"If it's math, ensure it's also within $...$ or a math environment. "
                    f"E.g., change to '{latex_content}' or '${latex_content}$'."
                )
    def get_errors(self) -> List[LinterError]:
        """Returns all collected linter errors."""
        # Sort errors by line number
        self.errors.sort(key=lambda x: x[0])
        return self.errors

def lint_markdown(markdown_content: str) -> List[LinterError]:
    """
    Main function to lint markdown content.
    Initializes the linter, runs checks, and returns errors.
    """
    if not markdown_content.strip():
        return []

    linter = MarkdownLinter(markdown_content)
    linter.run_checks() # This will call the specific check methods once implemented
    return linter.get_errors()

if __name__ == '__main__':
    test_md_content_empty = ""
    test_md_content_simple = """
# Title
This is `some code`.
This is a line.
    """

    print("--- Testing linter with empty content ---")
    errors_empty = lint_markdown(test_md_content_empty)
    if not errors_empty:
        print("OK: No errors for empty content as expected.")
    else:
        print(f"FAIL: Found errors in empty content: {errors_empty}")

    print("\n--- Testing linter with simple valid content (backtick check only) ---")
    # lint_markdown will call run_checks which calls _check_backtick_escaping
    errors_simple = lint_markdown(test_md_content_simple)

    if not errors_simple:
        print("OK: No errors for simple content as expected.")
    else:
        print(f"FAIL: Found errors in simple content: {errors_simple}")

    test_md_backticks = r"""
This has `\sum` and also `\alpha`_i.
And `\begin{align*}`.
Also a correct code block: `my_variable_name`.
A more complex one: `\Theta_L(z)`.
And `\sum_{v\in L}` (here `\in` is a valid command).
Simple case: `\test`
`\gamma_{ij}^k`
Nested: `\textit{\command_inside}`
Not an issue: `` `verbatim with \ backslash` `` (double backticks)
Not an issue: `text with a \ backslash` (no command)
    """
    print("\n--- Testing linter with backtick issues ---")
    errors_backticks = lint_markdown(test_md_backticks)

    if errors_backticks:
        print("Found potential backtick escaping issues:")
        for err_line, err_type, err_msg, err_sugg in errors_backticks:
            print(f"  Line {err_line}: [{err_type}] {err_msg} Suggestion: {err_sugg}")
    else:
        print("FAIL: No backtick errors found where expected.")

    # Expected for test_md_backticks:
    # Line 2: `\sum`
    # Line 2: `\alpha`_i
    # Line 3: `\begin{align*}`
    # Line 5: `\Theta_L(z)`
    # Line 6: `\sum_{v\in L}` (containing `\in`)
    # Line 7: `\test`
    # Line 8: `\gamma_{ij}^k`
    # Line 9: `\textit{\command_inside}`

    print("\n--- Testing linter with math delimiter issues ---")
    test_md_math_delimiters = r"""
Correct: $a+b=c$ and \(x^2\) also \[ \sum_{i=1}^n i = \frac{n(n+1)}{2} \] and $$ \text{display} $$
Unclosed $: $x+y
Unclosed \(: \(z-1
Unclosed \[ : \[ \alpha \]
Unclosed $$: $$ \beta
Mismatched: $x+y\)
Mismatched: \(x+y]$
Mismatched: \[x+y)$
Unmatched closer: x + y$  (previous $ was closed or never opened) -> this case is tricky, depends on $ toggle logic
Unmatched closer: x + y\)
Unmatched closer: x + y\]
Suspicious mix: $ (\alpha+\beta) $ (should be $ (\alpha+\beta) $ or \($\alpha+\beta$\) ) -> This is tricky.
Suspicious mix: \( [ a,b ] \) -> This is also tricky. For now, $ with \( or \[ is flagged.
Line with escaped \$ dollar and escaped \( paren.
This is $a an unclosed one.
And this is \( another.
And $$ yet another.
And \[ final one.
Text then $ an opener.
Text then unmatched \) closer.
$dollar opener \( paren opener \) paren closer $ dollar closer -> OK
$dollar opener \[ bracket opener \] bracket closer $ dollar closer -> OK
\( paren opener $ dollar opener $ dollar closer \) paren closer -> Suspicious by current logic
\[ bracket opener $ dollar opener $ dollar closer \] bracket closer -> Suspicious
$$ display opener $ inline $ display closer $$ -> This is valid in some contexts, but might be flagged by simple mixing.
"""
    errors_math_delimiters = lint_markdown(test_md_math_delimiters)
    if errors_math_delimiters:
        print("Found potential math delimiter issues:")
        for err_line, err_type, err_msg, err_sugg in errors_math_delimiters:
            print(f"  Line {err_line}: [{err_type}] {err_msg} Suggestion: {err_sugg}")
    else:
        print("OK: No math delimiter errors found (or test cases need review if errors expected).")

    print("\n--- Testing linter with environment delimiter issues ---")
    test_md_env_delimiters = r"""
Correct:
\begin{itemize}
  \item Item 1
  \item Item 2
\end{itemize}

Unclosed begin:
\begin{align*}
  x = y + z

Mismatched end:
\begin{equation}
  E = mc^2
\end{align*}

Unmatched end:
  y = x
\end{foo}

Nested correct:
\begin{theorem}
  Statement.
  \begin{proof}
    Proof here.
  \end{proof}
\end{theorem}

Nested unclosed inner:
\begin{outer}
  \begin{inner}
    Content
\end{outer}

Nested mismatched inner:
\begin{another}
  \begin{yetanother}
    Content
  \end{badanother}
\end{another}
"""
    errors_env_delimiters = lint_markdown(test_md_env_delimiters)
    if errors_env_delimiters:
        print("Found potential environment delimiter issues:")
        for err_line, err_type, err_msg, err_sugg in errors_env_delimiters:
            print(f"  Line {err_line}: [{err_type}] {err_msg} Suggestion: {err_sugg}")
    else:
        print("OK: No environment delimiter errors found (or test cases need review).")

    print("\n--- Testing linter with common LaTeX command issues ---")
    test_md_common_issues = r"""
Double scripts: $x_a_b$, $y^c^d$, $z_1^2_3$ (mixed, may not be caught by simple check)
Correct scripts: $x_{ab}$, $y^{cd}$, $x_{a_b}$, $y^{c^d}$, $z_a^{b_c}$
No braces needed: $\sqrt x$, $\textbf A$, $\textit i$
Needs braces: $\sqrt xy$, $\textbf{long text}$, $\textit{another phrase}$
$\sqrt \alpha_1$ (needs braces for \alpha_1)
$\frac ab$ (fine)
$\frac 12$ (should be \frac{1}{2} - current \frac check is disabled)
$\frac \alpha\beta$ (should be \frac{\alpha}{\beta} - current \frac check is disabled)
$\emph word word$
"""
    errors_common_issues = lint_markdown(test_md_common_issues)
    if errors_common_issues:
        print("Found potential common LaTeX command issues:")
        for err_line, err_type, err_msg, err_sugg in errors_common_issues:
            print(f"  Line {err_line}: [{err_type}] {err_msg} Suggestion: {err_sugg}")
    else:
        print("OK: No common command issues found (or test cases need review).")


    print("\nLinter structure seems OK. Specific checks to be added.")
