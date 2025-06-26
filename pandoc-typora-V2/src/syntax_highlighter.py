# syntax_highlighter.py
import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt

def highlighting_rule(pattern, style_format):
    """Helper function to create a highlighting rule tuple."""
    return (re.compile(pattern), style_format)

class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # --- Text Styles/Formats ---
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#4E9A06")) # Chameleon Green
        header_format.setFontWeight(QFont.Bold)

        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        # bold_format.setForeground(QColor("#C4A000")) # Chameleon Yellow (for emphasis)

        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        # italic_format.setForeground(QColor("#C4A000"))

        bold_italic_format = QTextCharFormat()
        bold_italic_format.setFontWeight(QFont.Bold)
        bold_italic_format.setFontItalic(True)
        # bold_italic_format.setForeground(QColor("#C4A000"))

        strikethrough_format = QTextCharFormat()
        strikethrough_format.setFontStrikeOut(True)
        # strikethrough_format.setForeground(QColor("#888A85")) # Aluminium Grey

        inline_code_format = QTextCharFormat()
        inline_code_format.setBackground(QColor("#EEEEEC")) # Aluminium Grey Light
        inline_code_format.setForeground(QColor("#2E3436")) # Aluminium Grey Dark
        # inline_code_format.setFontFamily("monospace") # Consider setting a monospace font

        code_block_format = QTextCharFormat()
        code_block_format.setBackground(QColor("#F0F0F0")) # Lighter than inline
        code_block_format.setForeground(QColor("#000000"))
        # code_block_format.setFontFamily("monospace")

        link_text_format = QTextCharFormat()
        link_text_format.setForeground(QColor("#3465A4")) # Sky Blue
        link_text_format.setFontUnderline(True)

        link_url_format = QTextCharFormat() # For the (url) part
        link_url_format.setForeground(QColor("#729FCF")) # Lighter Sky Blue

        list_marker_format = QTextCharFormat()
        list_marker_format.setForeground(QColor("#75507B")) # Plum

        blockquote_format = QTextCharFormat()
        blockquote_format.setForeground(QColor("#888A85")) # Aluminium Grey
        blockquote_format.setFontItalic(True) # Common styling for blockquotes

        horizontal_rule_format = QTextCharFormat()
        horizontal_rule_format.setForeground(QColor("#BABDB6")) # Aluminium Grey Medium
        horizontal_rule_format.setFontWeight(QFont.Bold)

        fenced_div_marker_format = QTextCharFormat()
        fenced_div_marker_format.setForeground(QColor("#A40000")) # Scarlet Red Dark
        fenced_div_marker_format.setBackground(QColor("#F0F0F0"))


        # --- Highlighting Rules (Order Matters!) ---

        # Headers (ATX style: #, ##, ### etc.)
        self.highlighting_rules.append(highlighting_rule(r"^(#{1,6})\s+.*", header_format))

        # Blockquotes
        self.highlighting_rules.append(highlighting_rule(r"^\s*>\s+.*", blockquote_format))

        # Horizontal Rules (***, ---, ___)
        self.highlighting_rules.append(highlighting_rule(r"^\s*([-*_]){3,}\s*$", horizontal_rule_format))

        # List items (unordered: *, -, +; ordered: 1., 1))
        self.highlighting_rules.append(highlighting_rule(r"^\s*([*+-]|\d+[.)])\s+", list_marker_format))

        # Fenced Div Markers (::: div_name)
        # This will be a multi-line rule, handled in highlightBlock
        self.fenced_div_start_expr = re.compile(r"^(:::+)\s*([\w.-]+)?(.*)$") # Start: :::, ::: name, ::: name attr
        self.fenced_div_end_expr = re.compile(r"^(:::+)\s*$") # End: :::
        self.fenced_div_format = fenced_div_marker_format


        # --- Inline Patterns (Applied after block patterns) ---
        # These need to be applied carefully to avoid conflicts.
        # Order within this group also matters.

        # Bold and Italic (Combined first) - using __word__ or **word** for bold, _word_ or *word* for italic
        # This handles ***word*** or ___word___
        self.highlighting_rules.append(highlighting_rule(r"(\*\*\*|___)(.+?)\1", bold_italic_format))

        # Bold (**word** or __word__)
        self.highlighting_rules.append(highlighting_rule(r"(\*\*|__)(.+?)\1", bold_format))

        # Italic (*word* or _word_)
        # Negative lookbehind/lookahead might be needed for more complex cases to avoid intra-word underscores.
        # For now, simple non-greedy match.
        self.highlighting_rules.append(highlighting_rule(r"(\*|_)(.+?)\1", italic_format))

        # Strikethrough (~~word~~)
        self.highlighting_rules.append(highlighting_rule(r"(~~)(.+?)\1", strikethrough_format))

        # Inline Code (`code`)
        self.highlighting_rules.append(highlighting_rule(r"`(.+?)`", inline_code_format))

        # Links ([text](url "title") or ![alt text](image_url "title"))
        # Simplified: just [text](url) or ![text](url)
        self.highlighting_rules.append(highlighting_rule(r"!?\[(.*?)\]", link_text_format)) # Matches [text] or ![text]
        self.highlighting_rules.append(highlighting_rule(r"\((.*?)\)", link_url_format))   # Matches (url) or (image_url)

        # --- Multi-line states ---
        self.code_block_start_expr = re.compile(r"^```([\w+-]*)?$") # ``` or ```python
        self.code_block_end_expr = re.compile(r"^```$")
        self.code_block_format = code_block_format

    def highlightBlock(self, text):
        # --- Apply single-line block rules first ---
        for pattern, style_format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, style_format)

        self.setCurrentBlockState(0) # Default state

        # --- Handle multi-line fenced code blocks (```) ---
        in_code_block = (self.previousBlockState() == 1)

        if not in_code_block:
            match = self.code_block_start_expr.match(text)
            if match:
                self.setCurrentBlockState(1) # Enter code block state
                self.setFormat(0, len(text), self.code_block_format)
                # Optionally, format the ``` part differently or the language identifier
                # self.setFormat(match.start(0), match.end(0) - match.start(0), some_other_format)
        else: # We are in a code block
            match = self.code_block_end_expr.match(text)
            if match:
                self.setCurrentBlockState(0) # Exit code block state
                self.setFormat(0, len(text), self.code_block_format) # Format this closing line too
            else:
                self.setFormat(0, len(text), self.code_block_format) # Format the entire line as code
            return # Don't apply other rules inside code blocks

        # --- Handle multi-line fenced divs (:::) ---
        # State 2 for inside a fenced div
        in_fenced_div = (self.previousBlockState() == 2)

        if not in_fenced_div:
            match = self.fenced_div_start_expr.match(text)
            if match:
                self.setCurrentBlockState(2) # Enter fenced div state
                # Format the opening ::: marker
                self.setFormat(match.start(1), match.end(1) - match.start(1), self.fenced_div_format)
                if match.group(2): # If there's a name
                     self.setFormat(match.start(2), match.end(2) - match.start(2), self.fenced_div_format) # Style name
                # The rest of the line (attributes) could be styled too if needed
        else: # We are in a fenced div
            match = self.fenced_div_end_expr.match(text)
            if match:
                self.setCurrentBlockState(0) # Exit fenced div state
                self.setFormat(match.start(1), match.end(1) - match.start(1), self.fenced_div_format)
            else:
                # Optionally, apply a different background or style to content within fenced divs
                # For now, just the markers are distinct.
                # If you want the content inside styled, you'd apply a format here.
                # self.setFormat(0, len(text), some_fenced_div_content_format)
                pass # Content inside div is not specially formatted beyond markers for now
                # Re-apply inline rules for content inside divs if desired
                # for pattern, style_format in self.highlighting_rules:
                #     if pattern in [self.bold_rule, self.italic_rule, ...]: # only inline ones
                #         for m in pattern.finditer(text):
                #             self.setFormat(m.start(), m.end() - m.start(), style_format)

        # Re-apply inline rules if not in a code block (already returned if in code block)
        # This is because block-level formatting (like code block) should take precedence.
        # And multi-line processing might have cleared previous formats.
        # Note: This simple re-application might not be perfect for overlapping inline styles
        # within lines that are also part of multi-line blocks (e.g., bold inside a div).
        # QSyntaxHighlighter applies formats sequentially.
        if self.currentBlockState() == 0: # Only apply if not in a special multi-line state handled above
            for pattern, style_format in self.highlighting_rules:
                # Avoid re-applying block-level rules that match ^ (start of line)
                # This is a simplification; a more robust way is to separate block and inline rules strictly.
                if not pattern.pattern.startswith('^'):
                    for match in pattern.finditer(text):
                        start, end = match.span()
                        self.setFormat(start, end - start, style_format)

# Example usage (for testing if run directly):
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
    app = QApplication([])

    editor = QTextEdit()
    highlighter = MarkdownSyntaxHighlighter(editor.document())

    test_text = """
# Header 1
## Header 2

This is **bold** and _italic_ and ***bold italic***.
And ~~strikethrough~~.

`inline code`

```python
def hello():
    print("Hello, world!")
```

Another paragraph.
* List item 1
  * Nested list item
+ List item 2
- List item 3
1. Ordered item 1
2. Ordered item 2

> This is a blockquote.
> It can span multiple lines.

---

[This is a link](http://example.com)
![This is an image](http://example.com/image.png)

::: warning
This is a warning div.
With **bold** text inside.
:::

Another line of text.
    """
    editor.setPlainText(test_text)

    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(editor)
    window.setLayout(layout)
    window.show()

    app.exec()
