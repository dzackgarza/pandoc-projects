import pytest
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextDocument # For type hinting
from src.syntax_highlighter import MarkdownSyntaxHighlighter

@pytest.fixture
def editor_with_highlighter():
    """Fixture to provide a QTextEdit with the MarkdownSyntaxHighlighter."""
    editor = QTextEdit()
    # The highlighter needs a QTextDocument, which a QTextEdit has.
    highlighter = MarkdownSyntaxHighlighter(editor.document())
    return editor, highlighter

@pytest.mark.smoke
def test_highlighter_instantiation(editor_with_highlighter):
    """Test if the MarkdownSyntaxHighlighter can be instantiated."""
    editor, highlighter = editor_with_highlighter
    assert highlighter is not None
    assert highlighter.document() == editor.document()

@pytest.mark.parametrize("markdown_text, rule_name_check", [
    ("# Header 1", "header_format"),
    ("## Header 2", "header_format"),
    ("**bold text**", "bold_format"),
    ("_italic text_", "italic_format"),
    ("`inline code`", "inline_code_format"),
    ("```python\ndef test():\n    pass\n```", "code_block_format"), # Multi-line
    ("::: warning\nThis is a div\n:::", "fenced_div_format"), # Multi-line
    ("> blockquote", "blockquote_format"),
    ("* list item", "list_marker_format"),
    ("---", "horizontal_rule_format"),
    ("[link](url)", "link_text_format"), # Also link_url_format
])
def test_basic_highlighting_rules_exist(editor_with_highlighter, markdown_text, rule_name_check):
    """
    Test that basic rule types are present in the highlighter.
    This is a conceptual check; it doesn't verify actual highlighting application,
    but that structures for these formats are defined.
    A more thorough test would involve checking QTextCharFormat attributes after highlighting.
    """
    editor, highlighter = editor_with_highlighter

    # Check if a format corresponding to the rule exists (simplistic check)
    # For instance, check if 'header_format' is an attribute of the highlighter
    assert hasattr(highlighter, rule_name_check)

    # Simulate highlighting (this won't directly check colors but ensures no crashes)
    # To properly test, one would need to inspect the QTextDocument's formatting.
    editor.setPlainText(markdown_text)
    highlighter.rehighlight()
    # No explicit assert here for visual output, but ensures process runs.

def test_code_block_highlighting_state(editor_with_highlighter):
    """Test multi-line code block state changes."""
    editor, highlighter = editor_with_highlighter
    doc = editor.document()

    editor.setPlainText("```python\nprint('hello')\n```")
    highlighter.rehighlight()

    # First line (```python) should enter code block state
    block1 = doc.findBlockByNumber(0)
    highlighter.highlightBlock(block1.text()) # Manually trigger for this block
    assert highlighter.currentBlockState() == 1 # State 1 for in_code_block

    # Second line (print('hello')) should be in code block state
    block2 = doc.findBlockByNumber(1)
    # Set previous state for context, as highlightBlock uses it
    highlighter.previousBlockState = 1
    highlighter.highlightBlock(block2.text())
    assert highlighter.currentBlockState() == 1

    # Third line (```) should exit code block state
    block3 = doc.findBlockByNumber(2)
    highlighter.previousBlockState = 1
    highlighter.highlightBlock(block3.text())
    assert highlighter.currentBlockState() == 0 # State 0 for default

# TODO: Add more detailed tests for:
# - Correct QColor and QFont application for each rule.
# - Overlapping rules (e.g., bold inside a header).
# - Edge cases (empty input, very long lines).
# - Pandoc specific syntax if not covered by general markdown (e.g. fenced div attributes).
# - Fenced div state changes similar to code block test.
