import re
from typing import List, Tuple, Dict, Any
# Import get_markdown_ast from debugger.py if it's in the same package
# For now, assuming it might be called from a context where debugger.get_markdown_ast is available
# If running this file directly, you'd need to adjust imports or mock it.
# from .debugger import get_markdown_ast # Use this if part of a package

def get_source_pos(element: Dict[str, Any]) -> Tuple[int, int, int, int] | None:
    """
    Extracts the source position (start line, start col, end line, end col)
    from a Pandoc AST element if available in its metadata.
    Pandoc typically adds this as:
    "meta": {
        ...
        "sourcepos": [
            [start_line, start_col],
            [end_line, end_col]
        ]
    }
    Or directly in the element's attributes for some versions/formats.
    This function needs to be robust to find it.
    """
    if not isinstance(element, dict):
        return None

    # Check common locations for source position information
    # 1. In element attributes (e.g. for CodeBlock)
    #    Attr = [identifier, [classes], [[key, val]]]
    #    Example: ["", [], [["sourcepos","1:1-3:3"]]]
    if 'c' in element and len(element['c']) > 0:
        attrs = element['c'][0]
        if isinstance(attrs, list) and len(attrs) > 2 and isinstance(attrs[2], list):
            for key, val in attrs[2]:
                if key == "sourcepos" and isinstance(val, str):
                    # Parse "SL:SC-EL:EC"
                    match = re.match(r"(\d+):(\d+)-(\d+):(\d+)", val)
                    if match:
                        return int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))

    # 2. In 'meta' dictionary, often part of a top-level block element's 'c'
    #    element = { "t": "Para", "c": [ { "t": "Str", "c": "Text", "meta": { "sourcepos": ...}}]}
    #    This is less common for block elements themselves, more for inlines.
    #    The more reliable source for blocks is often passed down or needs to be inferred.

    # 3. Pandoc >= 2.11 often puts it in the second element of a tuple for blocks
    #    e.g. ["Header", LEVEL, ATTR, INLINES] where ATTR can have sourcepos
    #    e.g. ["Para", INLINES] -> need to check INLINES
    #    For block elements, the source position is usually in the attributes part
    #    of the block structure. For example, for a Para, it's not directly on the Para,
    #    but on the inlines within it. We are interested in block-level units.

    # For now, this simplified version focuses on Attr as it's common for explicit sourcepos.
    # A more robust solution would traverse known AST structures.
    return None


def get_block_source_positions(ast: Dict[str, Any]) -> List[Tuple[int, int]]:
    """
    Extracts start and end line numbers for each top-level block element from the Pandoc AST.
    This aims to identify logical units.

    Args:
        ast: The Pandoc AST as a Python dictionary.

    Returns:
        A list of tuples, where each tuple is (start_line, end_line) for a block.
        Returns an empty list if AST is invalid or no source positions found.
    """
    if not ast or 'blocks' not in ast or not isinstance(ast['blocks'], list):
        return []

    positions = []
    for block in ast['blocks']:
        if not isinstance(block, dict) or 't' not in block:
            continue

        # Pandoc >= 2.11 often includes attributes as the second item in content list for blocks
        # e.g. block['c'][0] for attributes if block['c'] is a list [attrs, content]
        # or directly in block['c'] if it's like [level, attrs, content] for Header
        attrs = None
        content_tuple = block.get('c')

        if isinstance(content_tuple, list) and len(content_tuple) > 0:
            # Case 1: Element like Para, Div, Plain - attrs might be on inlines or not directly present
            # We need to parse the "sourcepos" attribute if present.
            # Example: CodeBlock ["CodeBlock", [ID, [CLASSES], [[KEY,VALUE_PAIRS]]], "code"]
            # The ATTR part is content_tuple[0]
            if block['t'] in ["CodeBlock", "Header", "Div", "BlockQuote", "Table"]: # Elements that typically have Attr
                 if len(content_tuple) > 0 and isinstance(content_tuple[0], list): # Attr is usually the first or second element
                    attr_list = content_tuple[0] # For CodeBlock, Header (after level)
                    if block['t'] == "Header" and len(content_tuple) > 1: # Header: [level, attr, inlines]
                        attr_list = content_tuple[1]

                    if isinstance(attr_list, list) and len(attr_list) > 2 and isinstance(attr_list[2], list):
                        for key, val in attr_list[2]: # key-value pairs
                            if key == "sourcepos" and isinstance(val, str):
                                match = re.match(r"(\d+):(\d+)-(\d+):(\d+)", val)
                                if match:
                                    start_line, _, end_line, _ = map(int, match.groups())
                                    positions.append((start_line, end_line))
                                    # Skip to next block once position is found
                                    continue # to next block in ast['blocks']
            # If not found in Attr, or for elements like Para, List, try to infer from content
            # This part is tricky and often requires looking at the first and last inline element's sourcepos
            # For simplicity, we'll rely on blocks that explicitly carry `sourcepos` for now.
            # Pandoc's native markdown reader adds `sourcepos` attribute to blocks.

    # Filter out overlapping or invalid ranges (though less likely with direct sourcepos)
    # Sort by start line
    positions.sort(key=lambda x: x[0])

    # For elements like Para, OrderedList, BulletList, Pandoc might not attach `sourcepos`
    # directly to the block but to its contents. A more advanced version would recursively
    # find min/max line numbers from children.
    # For now, this function will primarily find positions for blocks like CodeBlock, Header, Div
    # if they have the `sourcepos` attribute.

    # A simple fallback or alternative: iterate through all elements recursively
    # and collect all sourcepos, then determine block boundaries. This is more complex.
    # The current approach relies on pandoc providing block-level sourcepos.
    # If pandoc is run with --sourcepos flag, it should provide this.
    # The get_markdown_ast in debugger.py needs to ensure pandoc is called with --sourcepos.
    # Let's assume for now `pandoc -t json --sourcepos` is used.

    # If positions list is empty, it means top-level `sourcepos` attributes were not found.
    # This could happen if pandoc version is old or if --sourcepos wasn't used.
    # Or if the markdown structure is unusual.
    return positions


def split_markdown_by_lines(markdown_string: str, lines_per_chunk: int) -> List[Tuple[str, Tuple[int, int]]]:
    """
    Splits markdown string into chunks of specified number of lines.

    Args:
        markdown_string: The markdown content.
        lines_per_chunk: Number of lines for each chunk.

    Returns:
        A list of tuples, where each tuple is (chunk_string, (start_line, end_line)).
        Line numbers are 1-indexed.
    """
    lines = markdown_string.splitlines(keepends=True) # Keep newlines to reconstruct accurately
    chunks = []
    current_line_number = 1
    for i in range(0, len(lines), lines_per_chunk):
        chunk_lines = lines[i:i + lines_per_chunk]
        chunk_str = "".join(chunk_lines)
        start_line = current_line_number
        end_line = current_line_number + len(chunk_lines) -1
        chunks.append((chunk_str, (start_line, end_line)))
        current_line_number += len(chunk_lines)
    return chunks


def split_markdown_by_ast_blocks(markdown_string: str, ast: Dict[str, Any]) -> List[Tuple[str, Tuple[int, int]]]:
    """
    Splits markdown string into chunks based on AST block source positions.

    Args:
        markdown_string: The full markdown content.
        ast: The Pandoc AST of the markdown content (expected to have source positions).

    Returns:
        A list of tuples, where each tuple is (chunk_string, (start_line, end_line)).
        Returns empty list if AST positions are not found or on error.
    """
    source_positions = get_block_source_positions(ast)
    if not source_positions:
        # Fallback or error
        return []

    lines = markdown_string.splitlines(keepends=True)
    chunks = []

    for start_line, end_line in source_positions:
        if start_line == 0: # Skip if source pos seems invalid (0-indexed from pandoc sometimes)
            continue
        # Adjust to 0-indexed for list slicing, lines are 1-indexed from pandoc
        chunk_lines = lines[start_line - 1 : end_line]
        chunk_str = "".join(chunk_lines)
        chunks.append((chunk_str, (start_line, end_line)))

    return chunks


if __name__ == '__main__':
    # This import is tricky for standalone execution vs package execution.
    # For direct testing, we might need to mock or adjust path.
    try:
        from debugger import get_markdown_ast, compile_markdown_to_pdf # If in same dir for testing
    except ImportError:
        # Mock function if debugger.py is not directly accessible
        print("Warning: debugger.py not found, using mock get_markdown_ast for testing splitter.")
        def get_markdown_ast(md_str, use_sourcepos=True): # Add use_sourcepos
            # A very basic mock AST structure for testing
            if "```" in md_str and "Header" in md_str: # Crude check for content
                 # Simulate sourcepos for a header and a code block
                return {
                    "pandoc-api-version": [1, 22, 2, 1],
                    "meta": {},
                    "blocks": [
                        {
                            "t": "Header",
                            "c": [1, ["my-header", [], [["sourcepos", "1:1-1:15"]]], [{"t": "Str", "c": "Test"}, {"t": "Space"}, {"t": "Str", "c": "Header"}]]
                        },
                        {
                            "t": "Para", # Para often doesn't have sourcepos directly
                            "c": [{"t": "Str", "c": "Some", "meta": {"sourcepos": [[2,1],[2,4]]}}, {"t": "Space"}, {"t": "Str", "c": "text.", "meta": {"sourcepos": [[2,6],[2,10]]}}]
                        },
                        {
                            "t": "CodeBlock",
                            "c": [["", ["python"], [["sourcepos", "4:1-6:3"]]], "print('hello')\npass"]
                        }
                    ]
                }, ""
            return None, "Mock AST Error"

    example_md = """# Test Header
Some text.

```python
print('hello')
pass
```

Another paragraph.
"""
    print("--- Testing line-based splitting ---")
    line_chunks = split_markdown_by_lines(example_md, 2)
    for chunk_str, (start, end) in line_chunks:
        print(f"Lines {start}-{end}:\n{chunk_str.strip()}")

    print("\n--- Testing AST-based splitting ---")
    # Note: get_markdown_ast in debugger.py needs to be modified to pass --sourcepos
    # For now, the mock AST above includes it.
    # To run this properly, debugger.get_markdown_ast must call pandoc with --sourcepos
    ast_dict, ast_error = get_markdown_ast(example_md, use_sourcepos=True) # Assume modified get_markdown_ast

    if ast_dict:
        print("AST obtained successfully (mock or real).")
        # print(json.dumps(ast_dict, indent=2))
        ast_chunks = split_markdown_by_ast_blocks(example_md, ast_dict)
        if ast_chunks:
            for chunk_str, (start, end) in ast_chunks:
                print(f"AST Block (Lines {start}-{end}):\n{chunk_str.strip()}")
        else:
            print("Could not split by AST blocks (get_block_source_positions might need refinement or AST lacks sourcepos).")
            print("Ensure pandoc is called with --sourcepos for AST generation.")
    else:
        print(f"Failed to get AST: {ast_error}")

    # Example of how get_block_source_positions would be used
    if ast_dict:
        positions = get_block_source_positions(ast_dict)
        if positions:
            print("\nIdentified block source positions:")
            for start, end in positions:
                print(f"  Block from line {start} to {end}")
        else:
            print("\nNo block source positions identified by get_block_source_positions.")
            print("This indicates that either the AST doesn't have 'sourcepos' attributes at block level,")
            print("or the parsing logic in get_block_source_positions needs to be extended for this AST structure.")

    # Test with a more complex markdown including a list
    complex_md = """# Title

- Item 1
- Item 2
  - Subitem 2.1

```latex
\\begin{equation}
E=mc^2
\\end{equation}
```

Final paragraph.
"""
    print("\n--- Testing AST-based splitting on more complex MD ---")
    # This will likely fail to find many blocks if pandoc --sourcepos is not used
    # or if the AST structure for lists/paras doesn't have easily extractable block-level sourcepos
    # in the current get_block_source_positions implementation.
    complex_ast, complex_ast_err = get_markdown_ast(complex_md, use_sourcepos=True)
    if complex_ast:
        ast_chunks_complex = split_markdown_by_ast_blocks(complex_md, complex_ast)
        if ast_chunks_complex:
            for chunk_str, (start, end) in ast_chunks_complex:
                print(f"AST Block (Lines {start}-{end}):\n{chunk_str.strip()}")
        else:
            print("Could not split complex MD by AST blocks.")
            positions = get_block_source_positions(complex_ast)
            if not positions:
                print("get_block_source_positions returned no positions for complex_md.")
                print("This is common for elements like Para and List if not specifically handled or if sourcepos is missing.")
    else:
        print(f"Failed to get AST for complex_md: {complex_ast_err}")
