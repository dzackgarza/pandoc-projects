import logging
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.texmath import texmath_plugin # For \(...\), \[...\], and amsmath

# Configure logging to see token stream if needed, though direct print is often better for this.
# logging.basicConfig(level=logging.DEBUG)

from mdit_py_plugins.amsmath import amsmath_plugin

# Main parser setup for the proofer (dollarmath + amsmath)
md_proofer_parser = MarkdownIt().use(dollarmath_plugin).use(amsmath_plugin)

# Parser with texmath for comparison for \( \) and \[ \]
md_texmath_parser = MarkdownIt().use(texmath_plugin)


def print_tokens(parser_name, md_text, parser_instance):
    print(f"\n--- Tokens from: {parser_name} for text: ---\n{md_text}\n------------------------------------")
    tokens = parser_instance.parse(md_text)
    for token in tokens:
        print(f"Type: {token.type}, Tag: {token.tag}, Content: '{token.content}', Markup: '{token.markup}', Info: '{token.info}', Level: {token.level}, Children: {token.children is not None}")
        if token.children:
            for child in token.children:
                 print(f"  Child -> Type: {child.type}, Tag: {child.tag}, Content: '{child.content}', Markup: '{child.markup}', Level: {child.level}")

# --- Test Cases ---

# 1. Correct Inline Math
print_tokens("proofer_parser (dollar+amsmath)", "This is inline math: $a+b$.", md_proofer_parser)
print_tokens("texmath_parser", "This is inline math: \\(c=d\\).", md_texmath_parser) # To see how texmath handles \( \)
print_tokens("proofer_parser (dollar+amsmath)", "This is inline math with amsmath: \\(c=d\\).", md_proofer_parser) # How does dollar+amsmath handle it?

# 2. Correct Block Math
print_tokens("proofer_parser (dollar+amsmath)", "Block math:\n\n$$e=mc^2$$\n\nMore text.", md_proofer_parser)
print_tokens("texmath_parser", "Block math:\n\n\\[E=mc^2\\]\n\nMore text.", md_texmath_parser) # To see how texmath handles \[ \]
print_tokens("proofer_parser (dollar+amsmath)", "Block math with amsmath:\n\n\\[E=mc^2\\]\n\nMore text.", md_proofer_parser)

# 3. Unclosed/Mismatched Inline Math
print_tokens("proofer_parser (dollar+amsmath)", "Unclosed dollar: $a+b", md_proofer_parser)
print_tokens("proofer_parser (dollar+amsmath)", "Unclosed tex-style (amsmath): \\(c=d", md_proofer_parser)

# 4. Unclosed/Mismatched Block Math
print_tokens("proofer_parser (dollar+amsmath)", "Unclosed block dollar:\n\n$$e=mc^2", md_proofer_parser)
print_tokens("proofer_parser (dollar+amsmath)", "Unclosed block tex-style (amsmath):\n\n\\[E=mc^2", md_proofer_parser)

# 5. AMSMath environments
align_text_amsmath = """
An align environment:
\\begin{align}
a &= b \\\\
c &= d+e
\\end{align}
More text.
"""
print_tokens("proofer_parser (dollar+amsmath)", align_text_amsmath, md_proofer_parser)

align_text_unclosed_env_amsmath = """
Unclosed align:
\\begin{align}
a &= b
"""
print_tokens("proofer_parser (dollar+amsmath)", align_text_unclosed_env_amsmath, md_proofer_parser)

# 6. Test \text with amsmath
text_in_math_amsmath_block = "\\begin{equation} \\text{some text} \\sin x \\end{equation}"
print_tokens("proofer_parser (dollar+amsmath)", text_in_math_amsmath_block, md_proofer_parser)

text_in_math_dollar = "$ \\text{some text} \\sin x $" # dollarmath won't process \text
print_tokens("proofer_parser (dollar+amsmath)", text_in_math_dollar, md_proofer_parser)

# 7. Specific cases from roadmap
# x^23
print_tokens("proofer_parser (dollar+amsmath)", "$x^23$", md_proofer_parser)
# \frac{1}{2
print_tokens("proofer_parser (dollar+amsmath)", "$\\frac{1}{2$", md_proofer_parser) # Unclosed math
print_tokens("proofer_parser (dollar+amsmath)", "$\\frac{1}{2}$", md_proofer_parser) # Closed math, but unclosed frac
# \left( without \right)
print_tokens("proofer_parser (dollar+amsmath)", "$\\left( a+b \\right]$", md_proofer_parser) # Mismatched
print_tokens("proofer_parser (dollar+amsmath)", "$\\left( a+b $", md_proofer_parser)    # Unclosed at end of math

print("\nInvestigation script completed.")
