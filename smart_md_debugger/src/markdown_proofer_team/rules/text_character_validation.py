import re
from typing import List, Callable, Any, Tuple

# LinterError format: (line_number: int, error_type: str, message: str, suggestion: str | None)
# Error callback signature: error_callback(line_number, error_type, message, suggestion, token=None, line_content="")

# Characters that often need escaping in LaTeX text mode
LATEX_SPECIAL_CHARS_TEXT_MODE = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$', # Note: $ is also math delimiter, context is key. This is for literal $.
    '#': r'\#',
    '_': r'\_',
    '{': r'\{', # Not in Branch 1 list, but very common
    '}': r'\}', # Not in Branch 1 list, but very common
    '~': r'\~', # Or \textasciitilde{}
    '^': r'\^', # Or \textasciicircum{}
    '\\': r'\textbackslash{}', # Or \char`\\
}
# Simplified set from Branch 1 for initial implementation, focusing on non-markup contexts
BRANCH1_LATEX_SPECIAL_CHARS = {
    '&': r'\&',
    '%': r'\%',
    '#': r'\#', # Careful with headings
    '\x5f': r'\_', # '_' Careful with emphasis/strong
    '^': r'\^', # Careful with math superscripts
    '~': r'\~', # Careful with strikethrough
    '\\': r'\textbackslash{}'
}

# Problematic Unicode characters and their preferred ASCII/LaTeX replacements
PROBLEM_UNICODE_CHARS = {
    '“': ('"', ' स्मार्ट कोट्स “ -> "'), # Left double quote
    '”': ('"', ' स्मार्ट कोट्स ” -> "'), # Right double quote
    '‘': ("'", " स्मार्ट कोट्स ‘ -> '"), # Left single quote
    '’': ("'", " स्मार्ट कोट्स ’ -> '"), # Right single quote
    '—': ('---', 'em डॅश — -> ---'),   # Em dash
    '–': ('--', 'en डॅश – -> --'),    # En dash
    '\u00A0': ('~', 'अ-ब्रेकिंग स्पेस -> ~ (टिल्ड)'), # Non-breaking space (nbsp)
    # Add more as needed
}

# Regex for simple URL/email validation (very basic)
# This is a placeholder and can be significantly improved.
BASIC_URL_REGEX = re.compile(r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?", re.IGNORECASE)


# Basic email regex: something@something.something
# Does not cover all valid emails, but catches common forms and some malformed ones.
# Removed \b for use with fullmatch()
# Simplified for debugging:
BASIC_EMAIL_REGEX = re.compile(r".+@.+\..+")

# A more problematic one for "user@domain" without TLD (this one is for finditer, so \b is okay)
EMAIL_MISSING_TLD_REGEX = re.compile(r"""
    \b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\b(?!\.[a-zA-Z]{2,})
""", re.VERBOSE)


def check_latex_special_chars(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Suggests escaping special LaTeX characters when found in text content.
    Be careful about context provided by token type.
    """
    print(f"DEBUG_RULE_LATEX_CHARS_DICT: {BRANCH1_LATEX_SPECIAL_CHARS}") # Print the dictionary
    # print(f"DEBUG: check_latex_special_chars: Received {len(tokens)} tokens.") # DEBUG

    def process_text_token_for_latex_chars(text_token, parent_token_map):
        print(f"DEBUG_PROCESS_TEXT_TOKEN_LATEX: content='{text_token.content}', map={text_token.map}, parent_map={parent_token_map}") # DEBUG
        # Child text tokens might not have their own map, use parent's map for line number
        # text_token.map is [start_line, end_line] for top-level text tokens.
        # For children of 'inline', text_token.map is often None.
        # parent_token_map refers to the .map attribute of the parent 'inline' token.
        line_num_from_text_map = text_token.map[0] + 1 if text_token.map and text_token.map[0] is not None else None
        line_num_from_parent_map = parent_token_map[0] + 1 if parent_token_map and parent_token_map[0] is not None else 0

        line_num = line_num_from_text_map if line_num_from_text_map is not None else line_num_from_parent_map

        if not text_token.content: # Skip empty text tokens
            return

        # print(f"DEBUG: check_latex_special_chars: Processing text content: '{text_token.content}' on effective line ~{line_num} (text_map: {text_token.map}, parent_map: {parent_token_map})") # DEBUG

        for char_rule_loop, replacement_loop in BRANCH1_LATEX_SPECIAL_CHARS.items():
            # Removed the verbose DEBUG_LOOP_CHECK and DEBUG_FINALLY for brevity now
            # if text_token.content == "underscore":
            #     print(f"DEBUG_LOOP_CHECK: char_rule_loop='{char_rule_loop}', text_token.content='{text_token.content}'")
            #     is_present_check = char_rule_loop in text_token.content
            #     print(f"DEBUG_FINALLY: char_rule_loop is '{char_rule_loop}' (type {type(char_rule_loop)}), text_token.content is '{text_token.content}' (type {type(text_token.content)})")
            #     print(f"DEBUG_FINALLY: Is '{char_rule_loop}' in '{text_token.content}'? {is_present_check}")

            str_char_rule = str(char_rule_loop)
            str_char_rule = str(char_rule_loop)
            str_content = str(text_token.content)

            if str_char_rule in str_content: # Reverted to simple 'in' check
                i = 0
                while i < len(text_token.content):
                    found_idx = text_token.content.find(char_rule_loop, i)
                    if found_idx == -1:
                        break

                    backslashes = 0
                    temp_idx = found_idx - 1
                    while temp_idx >= 0 and text_token.content[temp_idx] == '\\':
                        backslashes += 1
                        temp_idx -= 1

                    is_unescaped = backslashes % 2 == 0
                    if is_unescaped:
                        context_snippet = text_token.content[max(0, found_idx-10):min(len(text_token.content), found_idx+10)]
                        error_callback(
                            line_number=line_num,
                            error_type="LATEX_SPECIAL_CHAR",
                            message=f"LaTeX special character '{char_rule_loop}' found unescaped in text: \"...{context_snippet}...\"",
                            suggestion=f"Escape it as '{replacement_loop}'. Current token content: '{text_token.content}'",
                            token=text_token
                        )
                    i = found_idx + 1

    for token in tokens:
        if token.type == 'text':
            # Top-level text token should have its own map.
            process_text_token_for_latex_chars(token, token.map)
        elif token.type == 'inline' and token.children:
            # print(f"DEBUG_RULE_LATEX_CHARS: Processing children of inline token (map: {token.map}):") # DEBUG # Keep this for structure
            for child_token_idx, child_token in enumerate(token.children):
                # print(f"DEBUG_RULE_LATEX_CHARS: Child {child_token_idx}: type='{child_token.type}', content='{str(child_token.content)}'") # DEBUG # Keep this for structure
                if child_token.type == 'text':
                    process_text_token_for_latex_chars(child_token, token.map) # Pass parent 'inline' token's map
        elif token.type in ['math_inline', 'math_block', 'math_inline_double', 'math_block_eqno',
                            'math_inline_tex', 'math_block_tex', # Added for texmath_plugin
                            'code_inline', 'code_block', 'html_inline', 'html_block', 'fence']:
            # fence is for ```code blocks```
            # math_inline_double is for $$...$$ from dollarmath plugin
            # math_block_eqno for amsmath environments
            # print(f"DEBUG: check_latex_special_chars: Skipping token type '{token.type}' for LaTeX char check.")
            pass
        else:
            # print(f"DEBUG: check_latex_special_chars: Ignoring token type {token.type} for this rule's main logic.")
            pass


def check_problematic_unicode_chars(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Suggests replacements for common problematic Unicode characters (smart quotes, dashes, etc.).
    """
    def process_text_token_for_unicode(text_token, parent_token_map):
        line_num_from_text_map = text_token.map[0] + 1 if text_token.map and text_token.map[0] is not None else None
        line_num_from_parent_map = parent_token_map[0] + 1 if parent_token_map and parent_token_map[0] is not None else 0
        line_num = line_num_from_text_map if line_num_from_text_map is not None else line_num_from_parent_map

        if not text_token.content: # Skip empty text tokens
            return

        # print(f"DEBUG: check_problematic_unicode_chars: Processing text content: '{text_token.content}' on effective line ~{line_num} (text_map: {text_token.map}, parent_map: {parent_token_map})") # DEBUG
        for char, (replacement, hint) in PROBLEM_UNICODE_CHARS.items():
            if char in text_token.content:
                error_callback(
                    line_number=line_num,
                    error_type="PROBLEM_UNICODE_CHAR",
                    message=f"Problematic Unicode character '{char}' ({hint}) found in text: '{text_token.content}'.",
                    suggestion=f"Replace with '{replacement}'.",
                    token=text_token
                )

    for token in tokens:
        if token.type == 'text':
            process_text_token_for_unicode(token, token.map)
        elif token.type == 'inline' and token.children:
            # print(f"DEBUG: check_problematic_unicode_chars: Processing children of inline token (map: {token.map}):") # DEBUG
            for child_token in token.children:
                if child_token.type == 'text':
                    process_text_token_for_unicode(child_token, token.map) # Pass parent 'inline' token's map
        elif token.type in ['math_inline', 'math_block', 'math_inline_double', 'math_block_eqno',
                            'math_inline_tex', 'math_block_tex', # Added for texmath_plugin
                            'code_inline', 'code_block', 'html_inline', 'html_block', 'fence']:
             # print(f"DEBUG: check_problematic_unicode_chars: Skipping token type '{token.type}' for unicode char check.")
             pass
        # else:
            # print(f"DEBUG: check_problematic_unicode_chars: Ignoring token type {token.type} for this rule's main logic.")


def check_malformed_links_emails(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Flags potentially malformed URLs or emails in text.
    This version checks text nodes. A more robust check might look at link tokens.
    """
    # print(f"DEBUG: check_malformed_links_emails: Starting. Tokens: {len(tokens)}")

    def check_autolink(token_to_check, current_line_num):
        if token_to_check.type == 'link_open' and token_to_check.info == 'auto':
            url_content = token_to_check.attrs.get('href', '')
            # print(f"DEBUG: links_emails: Autolink found: href='{url_content}', line {current_line_num}")
            if url_content.startswith('mailto:'): # Autolinked email
                email_part = url_content[7:]
                match_result = BASIC_EMAIL_REGEX.fullmatch(email_part)
                # print(f"DEBUG: links_emails: Email autolink part: '{email_part}', Regex fullmatch result: {bool(match_result)}")
                if not match_result:
                    # print(f"DEBUG: links_emails: MALFORMED_EMAIL_AUTOLINK: '{email_part}' for token on line {current_line_num}")
                    error_callback(
                        line_number=current_line_num,
                        error_type="MALFORMED_EMAIL_AUTOLINK",
                        message=f"Potentially malformed email in autolink: '<{url_content}>'.",
                        suggestion="Verify the email address format (e.g., user@example.com).",
                        token=token_to_check
                    )
            else: # Autolinked URL
                match_result = BASIC_URL_REGEX.fullmatch(url_content)
                condition_is_true = not match_result # Store the condition
                print(f"DEBUG_RULE_URL_CHECK: url='{url_content}', match_result={bool(match_result)}, evaluated_condition={condition_is_true}") # DEBUG
                if condition_is_true:
                    print(f"DEBUG_INSIDE_RULE: BAD_URL_AUTOLINK: Entered IF for '{url_content}'. Calling CB.")
                    error_callback(
                        line_number=current_line_num,
                        error_type="MALFORMED_URL_AUTOLINK",
                        message=f"Potentially malformed URL in autolink: '<{url_content}>'.",
                        suggestion="Verify the URL format.",
                        token=token_to_check
                    )
            return True # Indicate autolink was processed
        return False

    def process_text_for_email_issues(text_token, parent_token_map):
        line_num_from_text_map = text_token.map[0] + 1 if text_token.map and text_token.map[0] is not None else None
        line_num_from_parent_map = parent_token_map[0] + 1 if parent_token_map and parent_token_map[0] is not None else 0
        line_num = line_num_from_text_map if line_num_from_text_map is not None else line_num_from_parent_map

        if not text_token.content: return

        # Avoid re-processing content that is clearly part of a link scheme handled by autolinks
        if text_token.content.startswith(("mailto:", "http:", "https:", "ftp:")): # TODO: This check might be too simple if text can be "mailto:foo" then " bar"
            return

        # print(f"DEBUG_EMAIL_RULE_CONTENT_REPR: repr(text_token.content) = {repr(text_token.content)}") # DEBUG
        # print(f"DEBUG: check_malformed_links_emails (text part): Processing text content: '{text_token.content}' on effective line ~{line_num} (text_map: {text_token.map}, parent_map: {parent_token_map})")
        for match in EMAIL_MISSING_TLD_REGEX.finditer(text_token.content):
            matched_email_text = match.group(0)
            email_match_result = BASIC_EMAIL_REGEX.fullmatch(matched_email_text)
            condition_is_true = not email_match_result # Store the condition
            # print(f"DEBUG_RULE_PLAIN_EMAIL_CHECK: text='{matched_email_text}', match_result={bool(email_match_result)}, evaluated_condition={condition_is_true}") # DEBUG
            if condition_is_true:
                # print(f"DEBUG_RULE_PLAIN_EMAIL_MATCH: Matched '{matched_email_text}', basic_regex_match={bool(email_match_result)}, calling_cb={condition_is_true}")
                error_callback(
                    line_number=line_num,
                    error_type="POTENTIAL_MALFORMED_EMAIL",
                    message=f"Potentially malformed email found in text: '{match.group(0)}'. It might be missing a top-level domain (e.g., .com, .org).",
                    suggestion="Verify the email address format.",
                    token=text_token
                )

    for token in tokens:
        # Determine line number for the current top-level token
        current_line_num = token.map[0] + 1 if token.map and token.map[0] is not None else 0
        # print(f"DEBUG: links_emails: Top-level Token: type={token.type}, info={getattr(token, 'info', '')}, map={token.map}, line_num={current_line_num}")

        # Check 1: Top-level token is an autolink
        if check_autolink(token, current_line_num):
            continue # Autolink processed, move to next top-level token

        # Check 2: Plain text processing (also inside inline children)
        if token.type == 'text':
            process_text_for_email_issues(token, token.map)
        elif token.type == 'inline' and token.children:
            # print(f"DEBUG: links_emails: Processing children of inline token (map: {token.map}, line: {current_line_num}):")
            for child_token in token.children:
                child_line_num = child_token.map[0] + 1 if child_token.map and child_token.map[0] is not None else current_line_num # Use parent's line if child has no map
                # print(f"DEBUG: links_emails: Child Token: type={child_token.type}, info={getattr(child_token, 'info', '')}, map={child_token.map}, effective_line={child_line_num}")
                if check_autolink(child_token, child_line_num): # Check if child is an autolink
                    continue
                if child_token.type == 'text':
                    process_text_for_email_issues(child_token, token.map) # Pass parent 'inline' token's map for context

        elif token.type in ['math_inline', 'math_block', 'math_inline_double', 'math_block_eqno',
                            'math_inline_tex', 'math_block_tex', # Added for texmath_plugin
                            'code_inline', 'code_block', 'html_inline', 'html_block', 'fence']:
            # print(f"DEBUG: links_emails: Skipping token type '{token.type}' for link/email checks.")
            pass # Skip these for link/email checks
            # Check for things that look like URLs but might be broken (e.g. http:/blah, www.site without TLD)
            # This is very heuristic. Example: find "http://" not followed by reasonable domain.
            # Or "www." not followed by domain.tld
            # This is complex and might be better handled by a dedicated URL validation library if high precision is needed.
            # For now, focusing on the autolink check above is more reliable.


def check_list_marker_consistency(tokens: List[Any], lines: List[str], error_callback: Callable[..., None]):
    """
    Rule: Detects inconsistent list markers (e.g., mixing '-' and '*' in the same list at the same level).
    markdown-it-py parser normalizes list markers in its token stream for unordered lists (bullet_list_open token has `markup` attribute like '-' or '*').
    For ordered lists, `ordered_list_open` has `markup` like '.' or ')'.
    We need to track the marker for the current list and see if it changes for items at the same level.
    """
    list_marker_stack = [] # Stores (level, marker_char, line_number)
    # print(f"DEBUG: check_list_marker_consistency: Starting. Tokens: {len(tokens)}")

    for i, token in enumerate(tokens):
        line_num = token.map[0] + 1 if token.map and token.map[0] is not None else 0
        # print(f"DEBUG: list_consistency: Token: type={token.type}, markup={token.markup}, level={token.level}, map={token.map}, line_num={line_num}")

        if token.type == "bullet_list_open" or token.type == "ordered_list_open":
            # print(f"DEBUG: list_consistency: Opened list {token.type} with marker '{token.markup}' at level {token.level}, line {line_num}")
            list_marker_stack.append({'level': token.level, 'marker': token.markup, 'type': token.type, 'line': line_num, 'first_item_marker': None})

        elif token.type == "list_item_open":
            # print(f"DEBUG: list_consistency: Opened list_item with marker '{token.markup}' at level {token.level}, line {line_num}")
            if list_marker_stack:
                # Ensure we are matching the current list level.
                # A list_item_open should correspond to the list on top of stack if levels match.
                # Markdown-it structure: bullet_list_open -> list_item_open -> paragraph_open -> inline -> text -> paragraph_close -> list_item_close ...
                # The list_item_open's level is N+1 compared to bullet_list_open's level N.
                # So, stack top level should be token.level - 1.

                current_list = None
                # Find the list this item belongs to by matching level.
                # list_item_open's level is the item's own level.
                # The parent list (bullet_list_open) has level `token.level - 1`.
                parent_list_level = token.level -1
                for lst in reversed(list_marker_stack):
                    # Match type based on typical bullet characters vs. ordered list characters in item markup
                    is_bullet_type_item = any(m in token.markup for m in ['-', '*', '+'])
                    expected_list_type = "bullet_list_open" if is_bullet_type_item else "ordered_list_open"

                    if lst['level'] == parent_list_level and lst['type'] == expected_list_type:
                        current_list = lst
                        break

                if not current_list:
                    # print(f"DEBUG: list_consistency: No matching parent list found on stack for item at level {token.level}. Stack: {list_marker_stack}")
                    continue

                item_marker = token.markup # This is the marker for THIS item. e.g. "-", "*", "1."

                # For bullet lists, item_marker is '-', '*', '+'.
                # For ordered lists, item_marker is '1.', '2)', etc. We only care about bullet list type consistency.
                if current_list['type'] == "bullet_list_open":
                    actual_bullet_char = item_marker # For bullet lists, token.markup on list_item_open is the bullet char.
                    if current_list['first_item_marker'] is None:
                        current_list['first_item_marker'] = actual_bullet_char
                        # print(f"DEBUG: list_consistency: Set first_item_marker for list (lvl {current_list['level']}) to '{actual_bullet_char}'")
                    elif actual_bullet_char != current_list['first_item_marker']:
                        # print(f"DEBUG: list_consistency: INCONSISTENCY! Item marker '{actual_bullet_char}' vs first '{current_list['first_item_marker']}'")
                        error_callback(
                            line_number=line_num,
                            error_type="INCONSISTENT_LIST_MARKER",
                            message=f"Inconsistent list item marker '{item_marker}' used at line {line_num}. "
                                    f"The list started with '{current_list['first_item_marker']}' at line {current_list['line']}.",
                            suggestion=f"Use consistent markers for all items in the same list (e.g., use only '{current_list['first_item_marker']}').",
                            token=token
                        )

        elif token.type == "bullet_list_close" or token.type == "ordered_list_close":
            if list_marker_stack:
                # Make sure we are closing the right level of list.
                # markdown-it-py should produce a balanced token stream, so stack should not be empty.
                # And token.level should match stack top's level.
                if list_marker_stack[-1]['level'] == token.level :
                    list_marker_stack.pop()
                else:
                    # This would indicate a token stream issue or logic error here.
                    # For now, assume valid stream and pop cautiously.
                    # Look for the matching level to pop if there's a mismatch (should not happen with correct parser)
                    for j in range(len(list_marker_stack) - 1, -1, -1):
                        if list_marker_stack[j]['level'] == token.level:
                            list_marker_stack = list_marker_stack[:j] # Pop all lists up to and including this level
                            break


# List of all rule functions in this module
RULES = [
    check_latex_special_chars,
    check_problematic_unicode_chars,
    check_malformed_links_emails,
    check_list_marker_consistency,
]

if __name__ == '__main__':
    # Example of how to test these rules individually (conceptual)
    from markdown_it import MarkdownIt

    # Dummy error callback for testing
    def dummy_error_reporter(line_number, error_type, message, suggestion, token=None, line_content=""):
        print(f"Error reported: L{line_number} ({token.tag if token else ''}:{token.type if token else ''}) - {error_type} - {message} - Suggestion: {suggestion}")
        if token:
            print(f"  Token content: '{token.content if token.content else token.type}'")

    md_parser = MarkdownIt().enable('strikethrough') # Enable strikethrough for ~ testing

    test_content_latex_chars = r"""
This has an ampersand & here.
And a percentage % sign.
A hash # symbol (not a heading).
An underscore _ for emphasis_or_literal. This_is_literal.
A caret ^ symbol.
A tilde ~ for strikethrough ~~stuff~~ or literal ~.
A backslash \ itself.
Escaped: \% and \_ should be fine.
Double escaped: \\% should be treated as literal \ followed by unescaped %.
"""
    print("\n--- Testing LaTeX Special Chars ---")
    tokens_latex = md_parser.parse(test_content_latex_chars)
    lines_latex = test_content_latex_chars.splitlines()
    check_latex_special_chars(tokens_latex, lines_latex, dummy_error_reporter)

    test_content_unicode = """
“Smart quotes” and ‘single smart quotes’.
An em—dash here. An en–dash too.
A non-breaking space. (NBSP pasted here)
Regular quotes "here" and 'apostrophe'.
"""
    print("\n--- Testing Problematic Unicode Chars ---")
    tokens_unicode = md_parser.parse(test_content_unicode)
    lines_unicode = test_content_unicode.splitlines()
    check_problematic_unicode_chars(tokens_unicode, lines_unicode, dummy_error_reporter)

    test_content_links_email = """
Good URL: <http://example.com/path>
Good email: <mailto:test@example.com>
Bad URL (autolink): <http//bad.url>
Bad email (autolink): <mailto:test@nodomain>
Plain text email missing TLD: contact me at user@server here.
Plain text valid email: my.email@example.co.uk is fine.
URL in text: check www.example.com for info.
URL in text: http://foo.bar/baz.
Malformed in text: user@domain only.
"""
    print("\n--- Testing Malformed Links/Emails ---")
    tokens_links = md_parser.parse(test_content_links_email)
    lines_links = test_content_links_email.splitlines()
    check_malformed_links_emails(tokens_links, lines_links, dummy_error_reporter)

    test_content_lists = """
- Item 1
- Item 2
* Item 3 (inconsistent)
- Item 4

Nested:
- Level 1 A
  * Level 2 A1 (ok, different list)
  * Level 2 A2
- Level 1 B
  - Level 2 B1 (ok, consistent with itself)

1. Ord Item 1
2. Ord Item 2
  - Bullet sub-item
  - Bullet sub-item
1. Ord Item 3 (continues outer)

* List A
  + Sublist B (ok)
  + Sublist B
* List A
  - Sublist C (ok)
  - Sublist C

- Mixed level markers:
  - item a1
  * item a2 (inconsistent with parent list's first item type if we were checking that)
    - item b1 (ok, new list)
    * item b2 (inconsistent with b1)
"""
    print("\n--- Testing List Marker Consistency ---")
    tokens_lists = md_parser.parse(test_content_lists)
    lines_lists = test_content_lists.splitlines()
    # Need to enable 'replacements' rule for markdown-it to correctly parse list item markups in some cases
    # md_parser_lists = MarkdownIt("commonmark", {'replacements': True}).enable('strikethrough')
    # tokens_lists = md_parser_lists.parse(test_content_lists)
    check_list_marker_consistency(tokens_lists, lines_lists, dummy_error_reporter)

    print("\nIndividual rule tests completed. Integrate with RulesManager and MarkdownProofer next.")
