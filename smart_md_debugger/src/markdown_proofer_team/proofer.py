from typing import List, Tuple, Dict, Any
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin # For $...$ and $$...$$
from mdit_py_plugins.amsmath import amsmath_plugin # For environments like {align}
from mdit_py_plugins.texmath import texmath_plugin # For \(...\) and \[...\]

# Define a structure for linter errors, consistent with existing LinterError if possible
# (line_number: int, error_type: str, message: str, suggestion: str | None)
LinterError = Tuple[int, str, str, str | None]

class MarkdownProofer:
    def __init__(self, rules_manager: Any = None): # RulesManager will be defined later
        """
        Initializes the Markdown Proofer.
        Uses markdown-it-py to parse content and applies various linting rules.
        """
        self.md_parser = (
            MarkdownIt("commonmark", {"typographer": True}) # Enable typographer for smart quotes etc. to test against
            .use(dollarmath_plugin, allow_labels=True, allow_space=True) # Handles both $...$ and $$...$$
            .use(amsmath_plugin) # For environments like {align}
            .use(texmath_plugin) # For \(...\) and \[...\]
            # Add other necessary plugins here, e.g. for \(...\) and \[...\] if not covered
            # Note: markdown-it-py's core handles \( \) and \[ \] if you enable the 'texmath' option during MarkdownIt init
            # or use a plugin that specifically handles them. Dollarmath and amsmath focus on $ and environments.
            # For now, let's assume $ and $$ are primary from dollarmath_plugin.
            # And explicit \(, \) , \[ , \] might need 'texmath' rule enabled in parser or another plugin.
            # Checking markdown-it-py docs, 'math_inline' and 'math_block' are core rules, but need enabling.
            # Let's try to enable them:
            .enable(['math_inline', 'math_block', 'table', 'strikethrough']) # Enable LaTeX style math, tables, and strikethrough
        )
        self.errors: List[LinterError] = []
        self.rules_manager = rules_manager # To manage and apply different rules

    def add_error(self, line_number: int, error_type: str, message: str, suggestion: str | None = None, token: Any = None, line_content: str = ""):
        """
        Adds an error to the list of found errors.
        Tries to get line number from token if available and line_number is not explicitly set.
        """
        # final_line_number = line_number
        # # Ensure line_number is an int, default to 0 if None or problematic
        # if not isinstance(final_line_number, int):
        #     print(f"Warning: Non-integer line_number ({final_line_number}) passed to add_error for {error_type}. Defaulting to 0.")
        #     final_line_number = 0
        #
        # if token and hasattr(token, 'map') and token.map and token.map[0] is not None :
        #      # If token has a map, it's often more reliable, especially for direct tokens.
        #      # However, the rule might have already calculated a better line_num for children of 'inline'.
        #      # Let's prioritize the passed line_number if it's valid (e.g. > 0 or not the default from a failed calculation)
        #      # For now, the logic in rules tries to set line_number correctly.
        #      pass

        print(f"DEBUG: MarkdownProofer.add_error (id(self)={id(self)}, id(self.errors)={id(self.errors)}) called: line={line_number}, type='{error_type}', msg='{message}'") # DEBUG
        self.errors.append((line_number, error_type, message, suggestion))
        print(f"DEBUG: MarkdownProofer.add_error: self.errors after append (len={len(self.errors)}) = {self.errors[-1] if self.errors else 'EMPTY'}") # DEBUG


    def proof_content(self, markdown_content: str) -> List[LinterError]:
        """
        Proofs the given Markdown content.
        1. Parses the content into tokens using markdown-it-py.
        2. Applies registered linting rules to these tokens.
        """
        self.errors = [] # Reset errors for each run

        if not markdown_content.strip():
            return []

        tokens = self.md_parser.parse(markdown_content)
        lines = markdown_content.splitlines(keepends=False)

        # DEBUG: Print all tokens for a given input
        if "sin(x) + cos(y)" in markdown_content or "Text with \\(unclosed tex math" in markdown_content : # Conditional debug for specific test
            print(f"DEBUG_PROOFER: Input: '''{markdown_content}'''")
            for i, token in enumerate(tokens):
                print(f"DEBUG_PROOFER: Token {i}: Type={token.type}, Tag={token.tag}, Content='{token.content}', Markup='{token.markup}', Map={token.map}, Level={token.level}, Info='{token.info}'")
                if token.children:
                    for j, child in enumerate(token.children):
                        print(f"  DEBUG_PROOFER: Child {j}: Type={child.type}, Tag={child.tag}, Content='{child.content}', Markup='{child.markup}', Level={child.level}")
            print("DEBUG_PROOFER: --- End of Tokens ---")


        if self.rules_manager:
            self.rules_manager.apply_rules(tokens, lines, self.add_error)
        else:
            # Basic placeholder if no rules manager is set up
            # This part will be replaced by calls to specific rule functions/classes
            # For example, iterate through tokens and apply checks directly or via a rules engine.
            # print("DEBUG: Parsed tokens:", tokens)
            pass

        # Sort errors by line number
        self.errors.sort(key=lambda x: x[0])
        return self.get_errors()

    def get_errors(self) -> List[LinterError]:
        """Returns all collected linter errors."""
        return self.errors

if __name__ == '__main__':
    from .rules_manager import RulesManager
    from .rules import ALL_RULES # Import combined list of rules

    rules_manager = RulesManager()
    for rule_func in ALL_RULES:
        rules_manager.add_rule(rule_func)

    proofer = MarkdownProofer(rules_manager=rules_manager)

    test_md_content_branch1 = r"""
# Branch 1 Test Document

This document tests basic text and character validation.

## Special LaTeX Characters
An ampersand: &
A percentage sign: %
A hash symbol here: # (not a heading)
An underscore for emphasis: _emphasis_ or for literal: this_is_literal.
A caret symbol: ^ (could be math $x^2$ or literal).
A tilde for strikethrough: ~~strikethrough~~ or literal: ~.
A backslash itself: \.
Escaped should be fine: \% and \_ and \#.
This is math: $a_b = c^2$. And display: $$ \sum_{i=0}^N i $$.
This is also math: \( \alpha \) and \[ \beta \]

## Problematic Unicode Characters
Smart quotes: “Hello” and ‘World’.
Em-dash: —
En-dash: –
Non-breaking space:  (this is an actual NBSP)
Regular quotes: "Okay" and 'Fine'.

## Malformed URLs/Emails
Good URL (autolink): <http://example.com/path>
Good email (autolink): <mailto:test@example.com>
Bad URL (autolink): <http//bad.url>
Bad email (autolink): <mailto:test@nodomain>
Email missing TLD in text: contact at user@server or user@localhost.
Valid email in text: send to my.email@sub.example.co.uk for details.
Another malformed: test@domain then space.

## List Marker Consistency
- Item 1
- Item 2
* Item 3 (inconsistent marker)
- Item 4

1. Ordered 1
2. Ordered 2
  * Sublist A (consistent)
  * Sublist B
  - Sublist C (inconsistent with A/B, but consistent with itself - new list)

- List X
  - Item X1
  + Item X2 (inconsistent with X1)
- List Y

## Escaped sequences
This has \\% (escaped backslash then percent) - should be literal '\%'
This has \\\~ (escaped backslash then escaped tilde) - should be literal '\~'
This has % but is it \% or just %? The rule should find the unescaped one.
This has _ but is it \_ or just _?
    """
    print(f"--- Testing MarkdownProofer with Branch 1 rules ---")
    errors = proofer.proof_content(test_md_content_branch1)

    if not errors:
        print("OK: No errors found. (Check if this is expected based on test content and rule logic)")
    else:
        print("\n--- Found Errors: ---")
        for error in errors:
            # (line_number: int, error_type: str, message: str, suggestion: str | None)
            print(f"L{error[0]}: [{error[1]}] {error[2]}")
            if error[3]:
                print(f"  Suggestion: {error[3]}")
        print(f"\nTotal errors: {len(errors)}")

    print("\n--- Testing parsing of math content specifically ---")
    math_test_content = r"""
Inline math $x^2 + y_i = \alpha$. Escaped dollar \$ not math.
Display math:
$$
\frac{a}{b} = \sum_{k=0}^N k^2
$$
Escaped display \$\$ not math.
LaTeX env:
\begin{align}
    E &= mc^2 \\
    F &= ma
\end{align}
Math with backslash paren: \( \sqrt{x} \) and block \[ \oint E \cdot dA \]
Escaped backslash paren: \\( not math \\) and \\[ not math \\]
    """
    # We just want to see the tokens for now, no specific errors from Branch 1 expected here unless text within math has issues.
    print("\nTokens for math content:")
    math_tokens = proofer.md_parser.parse(math_test_content)
    for t in math_tokens:
        print(f"Type: {t.type}, Tag: {t.tag}, Content: '{t.content}', Markup: '{t.markup}', Level: {t.level}, Line: {t.map[0] if t.map else 'N/A'}")
        # if t.children:
        #     print(f"  Children: {t.children}")


    print("\nMarkdownProofer Branch 1 validation run complete.")
