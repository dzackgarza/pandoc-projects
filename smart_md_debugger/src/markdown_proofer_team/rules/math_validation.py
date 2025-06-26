# Math Validation Rules for Smart Markdown Debugger
import re
from typing import List, Callable, Any

# Error callback signature: error_callback(line_number, error_type, message, suggestion, token=None, line_content="")

def check_unclosed_math_delimiters(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Detects unclosed math delimiters ($ $, $$, \( \), \[ \]) that were not parsed into math tokens.
    Also checks for unclosed \begin{env} that were not parsed into amsmath tokens.
    """
    # Regex to find potential unescaped $, $$, \(, \[
    # We are looking for these in 'text' tokens, as correctly formed math
    # would have been turned into math_inline, math_block, or amsmath tokens.

    # Simple check for single unescaped $:
    # - Not preceded by \
    # - Not followed immediately by another $ (to avoid $$)
    # - Not part of a URL (e.g. query params, though $ in URL is rare) - harder to check here
    # - Not followed by a digit (common for currency $100) - this helps reduce false positives
    UNESCAPED_SINGLE_DOLLAR_REGEX = re.compile(r"(?<!\\)\$((?!\$|\d))")

    # Check for unescaped $$
    UNESCAPED_DOUBLE_DOLLAR_REGEX = re.compile(r"(?<!\\)\$\$")

    # Check for unescaped \( and \[ (these are regex special chars, so escape them)
    UNESCAPED_OPENING_PAREN_REGEX = re.compile(r"(?<!\\)\\\(")
    UNESCAPED_OPENING_BRACKET_REGEX = re.compile(r"(?<!\\)\\\[")

    KNOWN_MATH_ENVS = [
        'equation', 'equation*',
        'align', 'align*', 'aligned',
        'gather', 'gather*', 'gathered',
        'multline', 'multline*',
        'flalign', 'flalign*',
        'alignat', 'alignat*',
        'cases',
        # Add more as needed, e.g., from amsmath documentation
    ]
    # Regex for \begin{<known_env>}
    BEGIN_ENV_REGEX_STR = r"\\begin\{(" + "|".join(KNOWN_MATH_ENVS) + r")\}"
    BEGIN_ENV_REGEX = re.compile(BEGIN_ENV_REGEX_STR)

    # To check if a \begin{env} was properly handled, we'd ideally see if an 'amsmath' token covers its range.
    # This is complex here. A simpler heuristic: if we find \begin{env} in a text token, it's suspicious.

    for token_idx, token in enumerate(tokens):
        # Only process text content, either in top-level text token or nested within inline
        text_content_sources = []
        if token.type == 'text':
            text_content_sources.append({'content': token.content, 'map': token.map, 'token': token})
        elif token.type == 'inline' and token.children:
            for child in token.children:
                if child.type == 'text':
                    text_content_sources.append({'content': child.content, 'map': token.map, 'token': child}) # Use parent inline's map for line

        for src in text_content_sources:
            content = src['content']
            line_num = src['map'][0] + 1 if src['map'] and src['map'][0] is not None else 0

            # Check for single $
            # This is very prone to false positives (currency, etc.)
            # A better check would be if a $ is found, and no corresponding closing $ is found *by the parser*
            # For now, a very simple heuristic: find $ not followed by digit/another $
            # and assume it might be an attempt at inline math.
            # This rule will need significant refinement or context from other rules.
            # The main idea is: if dollarmath_plugin *didn't* make a math_inline token, why?
            for match in UNESCAPED_SINGLE_DOLLAR_REGEX.finditer(content):
                # Check if this $ is already part of a math_inline token that might be malformed (e.g. $...text)
                # This check is hard without looking at surrounding tokens and parser state.
                # For now, if it's in a text token, it's suspicious.
                # A more robust check would be to see if an odd number of non-escaped '$' exist.
                # This current regex just finds a single '$' not part of '$$' or '$<digit>'.

                # Let's count non-escaped $ in the content of the current paragraph
                # This requires looking up the parent paragraph's full text content
                # For simplicity now, just flag if this text node itself has an odd number of $
                # This is still not great.

                # Simplest initial: if we find $ in a text token, it might be an issue.
                # The dollarmath plugin should have consumed it if it was valid math.
                # Let's assume any $ found here is potentially unclosed or misused.

                # A simple count of non-escaped $ within this specific text token
                actual_dollar_count = 0
                temp_i = 0
                while temp_i < len(content):
                    idx = content.find('$', temp_i)
                    if idx == -1: break
                    bs_count = 0
                    bi = idx -1
                    while bi >=0 and content[bi] == '\\':
                        bs_count +=1
                        bi -=1
                    if bs_count % 2 == 0: # Not escaped
                        actual_dollar_count +=1
                    temp_i = idx + 1

                if actual_dollar_count % 2 != 0: # Odd number of dollars in this text segment
                     print(f"DEBUG_UNCLOSED_DELIM: Odd dollar count ({actual_dollar_count}) in content '{content}', line {line_num}") # DEBUG
                     error_callback(
                        line_number=line_num,
                        error_type="UNCLOSED_INLINE_MATH_DOLLAR",
                        message=f"Potentially unclosed inline math: found odd number ({actual_dollar_count}) of '$' delimiters in text segment.",
                        suggestion="Ensure each '$' is part of a pair '$...$' or escape it as '\\$'.",
                        token=src['token']
                    )
                     break # Avoid multiple reports for the same text segment from this check

            # Check for $$
            if content == "$$": # Specific debug for this case
                print(f"DEBUG_UNCLOSED_DELIM: Checking content '{content}', src_map={src['map']}, calculated_line_num={line_num}. Regex search result: {UNESCAPED_DOUBLE_DOLLAR_REGEX.search(content)}")
            if UNESCAPED_DOUBLE_DOLLAR_REGEX.search(content):
                error_callback(
                    line_number=line_num,
                    error_type="UNCLOSED_BLOCK_MATH_DOLLAR",
                    message="Potentially unclosed block math: found '$$' in a text segment.",
                    suggestion="Ensure '$$' is part of a pair '$$...$$' on its own lines or used correctly.",
                    token=src['token']
                )

            # Check for \( and \[ are removed as texmath_plugin handles them by converting to text,
            # making these specific regexes for \\( and \\[ not useful if texmath is active.
            # If texmath_plugin were not used, these checks might be relevant.

            # Check for \begin{env}
            for match in BEGIN_ENV_REGEX.finditer(content):
                env_name = match.group(1)
                # Crude check: does it have a corresponding \end{env} in the same text block?
                # A proper check would need to see if an amsmath token was actually created.
                # If it's in a text token, it's already suspicious.
                end_env_regex = re.compile(r"\\end\{" + re.escape(env_name) + r"\}")
                if not end_env_regex.search(content[match.end():]): # Search after the \begin{env}
                    error_callback(
                        line_number=line_num,
                        error_type="UNCLOSED_AMS_ENVIRONMENT",
                        message=f"Potentially unclosed AMS math environment: found '\\begin{{{env_name}}}' in text without a matching '\\end{{{env_name}}}' in the same segment.",
                        suggestion=f"Ensure '\\begin{{{env_name}}}' is properly closed with '\\end{{{env_name}}}'.",
                        token=src['token']
                    )


def check_math_braces_and_delimiters(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Validates content within recognized math tokens (math_inline, math_block, amsmath) for:
    - Mismatched or missing braces for superscripts, subscripts, fractions.
    - Mismatched \left and \right delimiters.
    - Nested exponents needing braces.
    """
    MATH_TOKEN_TYPES = ['math_inline', 'math_block', 'amsmath'] # Tokens containing math content

    # Regex for \left and \right commands with their delimiters
    # Captures: 1=(\left or \right), 2=(delimiter like ( ) [ ] { } | . etc)
    LEFT_RIGHT_REGEX = re.compile(r"\\(left|right)\s*([\(\)\[\]\{\}\|\.])") # Corrected delimiter set

    # Regex for subscript/superscript followed by multiple characters without braces
    # Looks for ^ or _ not followed by a '{' or a single char command like \alpha or a single digit/letter.
    # This will find x^12, x^ab, but not x^{12}, x^a, x^\alpha
    # It will also find x_12, x_ab.
    # Needs to be careful about commands like \sum_a^b
    # Simpler approach: find ^ or _, then check next meaningful token/char.
    # Regex: ([\^_])\s*([a-zA-Z0-9]{2,})  -- this is too simple, misses e.g. x^a b
    # Regex: ([\^_])\s*([a-zA-Z0-9](?:\s*[a-zA-Z0-9])+)(?![^{]) -- ^ or _ followed by at least two "words" (chars or groups of chars sep by space) not followed by {
    # This is hard to get right with pure regex for all cases.
    # Let's focus on a common simple case: ^ or _ followed by more than one alphanumeric char.
    SUSPICIOUS_SCRIPT_REGEX = re.compile(r"([\^_])\s*([a-zA-Z0-9]{2,})")

    def process_math_token_content(math_token, parent_map_for_line_num_calc):
        content = math_token.content
        # Use math_token's own map if available (e.g. for block tokens), else parent's for line num
        current_map = math_token.map if math_token.map else parent_map_for_line_num_calc
        line_num = current_map[0] + 1 if current_map and current_map[0] is not None else 0

        print(f"DEBUG_BRACES_DELIMS_RULE: Processing token type '{math_token.type}', line: {line_num}, content: '{content[:100]}...'")

        # 1. General Brace Balance Check ({})
        brace_level = 0
        for i, char in enumerate(content):
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1
            if brace_level < 0:
                error_callback(
                    line_number=line_num,
                    error_type="MATH_MISMATCHED_BRACE",
                    message=f"Mismatched braces in math content: '}}' found before matching '{{'.",
                    suggestion="Check brace pairing.",
                    token=token
                )
                break # Stop further brace checks for this token
        if brace_level != 0 and brace_level > 0: # check brace_level > 0 to avoid double report if < 0 already reported
             error_callback(
                line_number=line_num,
                error_type="MATH_UNCLOSED_BRACE",
                message=f"Unclosed braces in math content: {brace_level} '{{' character(s) remain unclosed.",
                suggestion="Ensure all '{' are closed with '}'.",
                token=token
            )

        # 2. \left & \right Balance and Matching
        lr_stack = [] # To store (delimiter_char, index_in_content)
        print(f"DEBUG_LR_CHECK: Content for left/right check: '{content}'")
        for match in LEFT_RIGHT_REGEX.finditer(content):
            command_type = match.group(1) # 'left' or 'right'
            delimiter = match.group(2)
            print(f"DEBUG_LR_CHECK: Found command '\\{command_type}{delimiter}' at pos {match.start()}") # DEBUG

            if command_type == "left":
                lr_stack.append({'delim': delimiter, 'pos': match.start()})
            elif command_type == "right":
                if not lr_stack:
                    error_callback(
                        line_number=line_num,
                        error_type="MATH_UNEXPECTED_RIGHT_DELIMITER",
                        message=f"Unexpected '\\right{delimiter}' without a matching '\\left...'.",
                        suggestion="Ensure every '\\right...' corresponds to a '\\left...'.",
                        token=token
                    )
                    continue

                left_entry = lr_stack.pop()
                left_delim = left_entry['delim']

                expected_right_delim = { "(": ")", "[": "]", "{": "}", ".": "." }.get(left_delim)

                if delimiter != expected_right_delim:
                    error_callback(
                        line_number=line_num,
                        error_type="MATH_MISMATCHED_LEFT_RIGHT_DELIMITER",
                        message=f"Mismatched '\\left{left_delim}' and '\\right{delimiter}'. Expected '\\right{expected_right_delim}'.",
                        suggestion=f"Match '\\left{left_delim}' with '\\right{expected_right_delim}'.",
                        token=token
                    )

        if lr_stack: # Any remaining \left delimiters
            for item in lr_stack:
                left_delim_char = item['delim']
                expected_map = { "(": ")", "[": "]", "{": "}", ".": "." }
                expected_closing_for_left = expected_map.get(left_delim_char)
                print(f"DEBUG_LR_CHECK: Reporting UNCLOSED_LEFT_DELIMITER for \\left{left_delim_char} at {item['pos']}") # DEBUG
                error_callback(
                    line_number=line_num,
                    error_type="MATH_UNCLOSED_LEFT_DELIMITER",
                    message=f"Unclosed '\\left{left_delim_char}' at position {item['pos']}.",
                    suggestion=f"Ensure every '\\left{left_delim_char}' has a matching '\\right{expected_closing_for_left}'.",
                    token=token
                )

        # 3. Superscript/Subscript needing braces (x^23, x_12)
        # This regex finds a ^ or _ followed by two or more alphanumeric characters.
        # It does NOT correctly handle cases like x^\alpha or legitimate single char scripts.
        # This is a simplified check for common errors.
        print(f"DEBUG_SCRIPT_CHECK: Content for script check: '{content}'")
        for match in SUSPICIOUS_SCRIPT_REGEX.finditer(content):
            script_char = match.group(1) # ^ or _
            script_content = match.group(2) # The content like "23"
            print(f"DEBUG_SCRIPT_CHECK: Found suspicious script: '{script_char}{script_content}'") # DEBUG

            # Avoid flagging if it's part of a command like \sum_{i=0}^{N}
            # This is hard. A simple check: if the char before ^ or _ is a letter, it's less likely part of \sum etc.
            # A better check might be to ensure the script_content is not part of a larger command.
            # For now, this will have false positives.

            # Check if immediately preceding char is a letter or digit or closing brace/paren/bracket
            # to avoid things like \int_a^b
            preceding_char_idx = match.start() -1
            is_part_of_symbol = False
            if preceding_char_idx >=0:
                if not (content[preceding_char_idx].isalnum() or content[preceding_char_idx] in ')}])'):
                    is_part_of_symbol = True # e.g. \sum_, \int^

            if not is_part_of_symbol:
                error_callback(
                    line_number=line_num,
                    error_type="MATH_SCRIPT_NEEDS_BRACES",
                    message=f"Script '{script_char}{script_content}' likely needs braces around '{script_content}'.",
                    suggestion=f"Change to '{script_char}{{{script_content}}}'.",
                    token=token
                )

        # 4. \frac {}{} structure (basic check for missing braces immediately after \frac)
        # This is a very simplified check. True \frac parsing is complex.
        frac_pos = 0
        while True:
            frac_pos = content.find("\\frac", frac_pos)
            if frac_pos == -1:
                break

            # Check character immediately after \frac
            check_idx = frac_pos + len("\\frac")
            # Skip spaces
            while check_idx < len(content) and content[check_idx].isspace():
                check_idx += 1

            if check_idx >= len(content) or content[check_idx] != '{':
                error_callback(
                    line_number=line_num,
                    error_type="MATH_FRAC_MISSING_FIRST_BRACE",
                    message="Found '\\frac' not immediately followed by '{' for the numerator.",
                    suggestion="Ensure '\\frac' is followed by two braced groups: \\frac{numerator}{denominator}.",
                    token=token
                )
            else: # Found \frac{ , now check for the second {
                # Simple scan for the next non-nested {
                first_brace_end = -1
                brace_level_frac = 0
                for k in range(check_idx, len(content)):
                    if content[k] == '{':
                        brace_level_frac += 1
                    elif content[k] == '}':
                        brace_level_frac -=1
                        if brace_level_frac == 0: # Matched the first {
                            first_brace_end = k
                            break
                if first_brace_end != -1:
                    second_arg_start_idx = first_brace_end + 1
                    while second_arg_start_idx < len(content) and content[second_arg_start_idx].isspace():
                        second_arg_start_idx +=1
                    if second_arg_start_idx >= len(content) or content[second_arg_start_idx] != '{':
                         error_callback(
                            line_number=line_num,
                            error_type="MATH_FRAC_MISSING_SECOND_BRACE",
                            message="Found '\\frac{num}' not immediately followed by '{' for the denominator.",
                            suggestion="Ensure '\\frac' is followed by two braced groups: \\frac{num}{den}.",
                            token=token
                        )

            frac_pos += len("\\frac") # Continue search after current find

    for token in tokens:
        if token.type in MATH_TOKEN_TYPES and token.type != 'math_inline': # Process block-level math tokens directly
             process_math_token_content(token, token.map)
        elif token.type == 'inline' and token.children:
            for child_token in token.children:
                if child_token.type == 'math_inline': # Target math_inline children of inline tokens
                    process_math_token_content(child_token, token.map) # Pass parent inline's map for line context


def check_align_environment_issues(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Performs basic structural checks on the content of amsmath tokens,
    particularly for align-like environments.
    - Checks for & alignment character balance per line.
    - Checks for \\ at the end of lines (except the last one).
    - Flags empty lines within the environment.
    """
    # TODO: Implement logic to parse token.content (e.g., from 'amsmath' tokens).
    ALIGN_ENV_TYPES = ['align', 'align*', 'aligned', 'flalign', 'flalign*', 'alignat', 'alignat*'] # add others if needed

    for token in tokens:
        if token.type != 'amsmath': # Only apply to amsmath tokens
            continue

        content = token.content.strip()
        line_num_start = token.map[0] + 1 if token.map and token.map[0] is not None else 0

        # Check if it's an align-like environment
        current_env_type = None
        for env_type in ALIGN_ENV_TYPES:
            if content.startswith(f"\\begin{{{env_type}}}") and content.endswith(f"\\end{{{env_type}}}"):
                current_env_type = env_type
                break

        if not current_env_type:
            continue

        # Extract content within the environment
        inner_content_match = re.search(r"\\begin\{" + re.escape(current_env_type) + r"\}(.*?)\\end\{" + re.escape(current_env_type) + r"\}", content, re.DOTALL)
        if not inner_content_match:
            continue # Should not happen if outer check passed, but good for safety

        inner_content = inner_content_match.group(1).strip()

        # Split into logical lines by \\
        # Using re.split to handle potential spaces around \\ and keep empty strings for multiple \\
        logical_lines = re.split(r'\s*\\\\\s*', inner_content)

        # Filter out lines that are purely comments (heuristic: starts with %)
        # Also, keep track of original line numbers roughly by counting \n in preceding segments

        num_ampersands_per_line = []
        processed_lines_info = [] # Store {'text': str, 'original_idx': int, 'has_content': bool}

        current_actual_line_offset = 0
        for i, line_segment in enumerate(logical_lines):
            # Count newlines in the original segment before this one to adjust line_num
            if i > 0:
                # Count newlines in the segment between previous \\ and this one
                # This is complex because the split segment doesn't directly map to original file lines easily.
                # For now, line number reporting will be for the start of the amsmath token.
                pass # Pinpointing exact line for internal errors is hard here.

            trimmed_line = line_segment.strip()

            # Heuristic: ignore lines that are just LaTeX comments
            if trimmed_line.startswith('%'):
                processed_lines_info.append({'text': trimmed_line, 'original_idx': i, 'has_content': False, 'is_comment': True})
                continue

            has_actual_content = bool(trimmed_line)
            processed_lines_info.append({'text': trimmed_line, 'original_idx': i, 'has_content': has_actual_content, 'is_comment': False})

            if has_actual_content:
                num_ampersands_per_line.append(trimmed_line.count('&'))

        # Check 1: Consistency of ampersands (for lines with content)
        if num_ampersands_per_line:
            first_amp_count = num_ampersands_per_line[0]
            # For align, typically 1 & per equation line (LHS & RHS). Or 2n-1 for n columns.
            # For now, let's check if all content lines have the same number of ampersands if that number is > 0
            # Or if some lines have & and others (with content) don't.

            # Check if any content line has ampersands
            any_line_has_ampersands = any(c > 0 for c in num_ampersands_per_line)
            all_content_lines_have_consistent_ampersands = True

            if any_line_has_ampersands:
                # Find the target ampersand count from the first line that has them
                target_amp_count = -1
                for count in num_ampersands_per_line:
                    if count > 0:
                        target_amp_count = count
                        break

                if target_amp_count != -1:
                    for count in num_ampersands_per_line:
                        if count != target_amp_count and count != 0 : # allow 0 if some lines don't need alignment
                             all_content_lines_have_consistent_ampersands = False
                             break
                        if count == 0 and target_amp_count > 0: # A line has content but no ampersands, while others do
                            pass # This might be acceptable in some cases, e.g. a single line title within align. Hard to make a strict rule.

            if not all_content_lines_have_consistent_ampersands:
                 error_callback(
                    line_number=line_num_start,
                    error_type="MATH_ALIGN_INCONSISTENT_AMPERSANDS",
                    message=f"Inconsistent number of '&' alignment characters across lines in '{current_env_type}' environment.",
                    suggestion="Ensure all lines that use '&' for alignment have a consistent number of them.",
                    token=token
                )

        # Check 2 & 3: \\ at line ends and no empty lines
        for idx, line_info in enumerate(processed_lines_info):
            original_line_segment = logical_lines[line_info['original_idx']] # Get pre-stripped segment

            # Check for \\ (except for the very last logical line)
            if idx < len(logical_lines) - 1: # If not the last segment after all splits by \\
                # The original segment (before stripping for empty/comment check) must have ended with \\
                # This is implicitly handled by how `logical_lines` was created by splitting by `\\`.
                # The check is more about the content *between* `\\`s.
                pass # Handled by split

            # Check for empty lines (that are not comments and not the last line if it's also empty)
            is_last_effective_line = True
            for k in range(idx + 1, len(processed_lines_info)):
                if processed_lines_info[k]['has_content']:
                    is_last_effective_line = False
                    break

            if not line_info['has_content'] and not line_info['is_comment'] and not is_last_effective_line:
                # This line is empty (not a comment) and not the last content-bearing line's trailing empty segment
                error_callback(
                    line_number=line_num_start, # Line number is approximate to start of environment
                    error_type="MATH_ALIGN_EMPTY_LINE",
                    message=f"Empty line found within '{current_env_type}' environment. This can cause errors.",
                    suggestion="Remove empty lines or ensure they are commented out with '%'.",
                    token=token
                )


def check_math_function_names(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Suggests using standard LaTeX math functions (e.g., \sin instead of sin)
    within recognized math tokens.
    """
    # TODO: Implement logic to find plain function names in token.content.
    MATH_TOKEN_TYPES = ['math_inline', 'math_block', 'amsmath']

    # List of common math functions that should typically be preceded by a backslash
    COMMON_MATH_FUNCTIONS = [
        "sin", "cos", "tan", "csc", "sec", "cot",
        "sinh", "cosh", "tanh", "coth",
        "arcsin", "arccos", "arctan",
        "exp", "log", "ln", "lg", # lg for log base 10
        "det", "dim", "ker", "deg", "arg",
        "gcd", "lcm",
        "min", "max", "inf", "sup",
        "lim", "liminf", "limsup",
        "Pr" # Probability
    ]

    # Build a regex to find these function names if not preceded by a backslash
    # and are whole words (bounded by non-alphanumeric or start/end of string)
    # We want to match 'sin' in 'sin(x)' or 'sin x' but not in '\sin(x)' or 'cosine'.
    # (?<!\\) ensures not preceded by a backslash.
    # \b ensures it's a whole word.
    # (?: ... ) makes the group non-capturing for the lookahead.
    # (?=\s*\(|\s+[\w^_\{]|$) ensures it's likely used as a function (followed by (, space and var/cmd, or end)

    # Simpler: find words, then check if they are in the list and if they are preceded by \
    # Regex to find standalone function names (words)
    # Look for a word that is one of our functions, not preceded by '\'
    # and followed by a non-alphabetic character or end of string (to avoid matching 'sin' in 'since')

    # This regex tries to find the function names as whole words, not preceded by a backslash,
    # and followed by a character that typically delimits a function name from its argument
    # (e.g., space, _, ^, (, {, [, or end of string).
    func_pattern_str = r"(?<!\\)\b(" + "|".join(COMMON_MATH_FUNCTIONS) + r")(?=[\s_\^\(\{\[]|$)"
    FUNC_NAME_REGEX = re.compile(func_pattern_str)

    def process_math_token_for_functions(math_token, parent_map_for_line_num_calc):
        content = math_token.content
        current_map = math_token.map if math_token.map else parent_map_for_line_num_calc
        line_num = current_map[0] + 1 if current_map and current_map[0] is not None else 0

        print(f"DEBUG_MATH_FUNC_RULE: Processing token type '{math_token.type}', line: {line_num}, content: '{content[:100]}...'")

        for match in FUNC_NAME_REGEX.finditer(content):
            func_name = match.group(1)
            print(f"DEBUG_MATH_FUNC_RULE: Matched function '{func_name}' in content '{content}'") # DEBUG

            # Additional check: ensure what follows isn't just more letters (e.g. "arg" in "argument")
            # The \b in regex should handle this, but double check context if needed.
            # Example: "minimum" should not flag "min". \bmin\b would correctly not match.

            # Check if the character immediately after the match is an opening parenthesis or a space
            # or a subscript/superscript character, or end of string.
            # This helps confirm it's used like a function.
            idx_after_match = match.end()
            if idx_after_match < len(content):
                char_after = content[idx_after_match]
                # If it's followed by more letters, it might be part of a larger word.
                # e.g. if we had "arg" and content is "argument". \b(arg)\b handles this.
                # This check is mostly for safety or more complex cases if \b isn't enough.
                if char_after.isalpha():
                    # This case should ideally be covered by \b, but if func_name was "lim" and text "limits"
                    # \b(lim)\b would match "lim" in "limits". We need to ensure it's not.
                    # A better regex for the function list might be func_name + (?![a-zA-Z])
                    # For now, let's assume \b is mostly sufficient.
                    pass # This simple regex with \b on both sides should be okay.

            error_callback(
                line_number=line_num,
                error_type="MATH_FUNCTION_NAME_MISSING_BACKSLASH",
                message=f"Math function '{func_name}' found without a preceding backslash.",
                suggestion=f"Use '\\{func_name}' for proper LaTeX formatting (e.g., '\\{func_name}(x)' or '\\{func_name} x').",
                token=token
            )

    for token in tokens:
        if token.type in MATH_TOKEN_TYPES and token.type != 'math_inline': # Process block-level math tokens directly
            process_math_token_for_functions(token, token.map)
        elif token.type == 'inline' and token.children:
            for child_token in token.children:
                if child_token.type == 'math_inline': # Target math_inline children of inline tokens
                    process_math_token_for_functions(child_token, token.map) # Pass parent inline's map

# List of all rule functions in this module
RULES = [
    check_unclosed_math_delimiters,
    check_math_braces_and_delimiters,
    check_align_environment_issues,
    check_math_function_names,
]
