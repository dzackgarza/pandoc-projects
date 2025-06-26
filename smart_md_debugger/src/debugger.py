import subprocess
import json

def compile_markdown_to_pdf(markdown_string: str, output_pdf_path: str = "temp_output.pdf") -> tuple[bool, str]:
    """
    Compiles a given markdown string to PDF using pandoc.

    Args:
        markdown_string: The markdown content as a string.
        output_pdf_path: The path to save the output PDF.

    Returns:
        A tuple containing:
            - bool: True if compilation was successful, False otherwise.
            - str: Pandoc's stderr output (empty if successful, error message otherwise).
    """
    try:
        process = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "pdf", "-o", output_pdf_path],
            input=markdown_string,
            text=True,
            capture_output=True,
            check=False  # Do not raise exception on non-zero exit
        )
        if process.returncode == 0:
            return True, ""
        else:
            # Attempt to clean up common pandoc error messages
            error_message = process.stderr
            if "Error producing PDF" in error_message:
                # Try to find a more specific LaTeX error if possible
                # This is a heuristic and might need refinement
                latex_error_prefix = "! LaTeX Error:"
                if latex_error_prefix in error_message:
                    error_lines = error_message.splitlines()
                    for i, line in enumerate(error_lines):
                        if line.startswith(latex_error_prefix):
                            # Return the error line and the next few for context
                            return False, "\n".join(error_lines[i:i+3])
            return False, error_message
    except FileNotFoundError:
        return False, "Pandoc command not found. Please ensure pandoc is installed and in your PATH."
    except Exception as e:
        return False, f"An unexpected error occurred during pandoc execution: {str(e)}"

def get_markdown_ast(markdown_string: str, use_sourcepos: bool = True) -> tuple[dict | None, str]:
    """
    Gets the AST (Abstract Syntax Tree) of the markdown string using pandoc's JSON output.

    Args:
        markdown_string: The markdown content as a string.
        use_sourcepos: Whether to include source position information in the AST.

    Returns:
        A tuple containing:
            - dict | None: The AST as a Python dictionary, or None if an error occurred.
            - str: Pandoc's stderr output or an error message.
    """
    try:
        pandoc_command = ["pandoc", "-f", "markdown", "-t", "json"]
        if use_sourcepos:
            pandoc_command.append("--sourcepos")

        process = subprocess.run(
            pandoc_command,
            input=markdown_string,
            text=True,
            capture_output=True,
            check=False
        )
        if process.returncode == 0:
            try:
                ast = json.loads(process.stdout)
                return ast, ""
            except json.JSONDecodeError as e:
                return None, f"Error decoding pandoc JSON output: {str(e)}"
        else:
            return None, process.stderr
    except FileNotFoundError:
        return None, "Pandoc command not found. Please ensure pandoc is installed and in your PATH."
    except Exception as e:
        return None, f"An unexpected error occurred during pandoc AST generation: {str(e)}"

import tempfile
import os
import sys # Ensure sys is imported for sys.stderr

# To make splitter usable, we need to ensure its import works.
# This might require adjustments based on how the project is structured or run.
try:
    from .splitter import split_markdown_by_ast_blocks, split_markdown_by_lines
except ImportError:
    # Fallback for direct execution or if not run as part of a package
    from splitter import split_markdown_by_ast_blocks, split_markdown_by_lines


def find_error_ranges(markdown_content: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]], str]:
    """
    Identifies line ranges in the markdown content that cause compilation errors.

    Args:
        markdown_content: The full markdown string.

    Returns:
        A tuple containing:
            - good_ranges: List of (start_line, end_line) tuples that compile.
            - bad_ranges: List of (start_line, end_line) tuples that fail to compile.
            - initial_error: The error message from the first failed compilation of the whole document.
    """
    lines = markdown_content.splitlines(keepends=True)
    total_lines = len(lines)
    if total_lines == 0:
        return [], [], "No content to process."

    # Use a temporary file for pandoc outputs
    temp_pdf_file = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmpfile:
            temp_pdf_file = tmpfile.name

        # 1. Try to compile the whole document first
        full_compile_success, full_compile_error = compile_markdown_to_pdf(markdown_content, temp_pdf_file)
        if full_compile_success:
            return [(1, total_lines)], [], "" # Whole document is good

        # 2. Get AST to guide splitting
        ast, ast_error = get_markdown_ast(markdown_content)
        if not ast:
            # If AST parsing fails, we can't use AST-based splitting.
            # For now, we'll report this and could fall back to line-based, but that's less ideal.
            # A robust tool might try to recover or use simpler splitting.
            # However, if pandoc can't even produce JSON, it's a severe issue with the markdown.
            error_message = f"Failed to generate AST: {ast_error}. Cannot perform AST-based debugging."
            # Try to find a line number from pandoc's error if possible for the AST failure
            # This is a heuristic
            match = re.search(r"line (\d+), column \d+", ast_error)
            if match:
                line_num = int(match.group(1))
                return [], [(line_num, line_num)], error_message # Pinpoint the AST error line
            return [], [(1, total_lines)], error_message # Cannot pinpoint further

        # 3. Use AST blocks for initial splitting
        # Ensure splitter functions are available
        chunks = split_markdown_by_ast_blocks(markdown_content, ast)

        if not chunks:
            # Fallback to line-based splitting if AST splitting yields no chunks
            # This might happen if get_block_source_positions doesn't find suitable blocks
            # or if the markdown is very simple (e.g., one line).
            # Fallback to line-by-line splitting if AST splitting yields no chunks.
            # Ensure sys is imported at the top of the file if this print statement is to be used.
            # For now, assuming sys is available or error reporting might be simplified if it's not critical path.
            # Let's assume sys is imported at the top for stderr.
            print("Warning: AST-based splitting did not yield any usable chunks. Falling back to line-by-line splitting.", file=sys.stderr)
            # Using a small chunk size for line-based splitting, e.g., 1 line at a time.
            # This is less ideal than AST but better than giving up.
            chunks = split_markdown_by_lines(markdown_content, 1) # 1 line per chunk
            if not chunks: # Should not happen if markdown_content is not empty
                 print("Error: Line-based splitting also yielded no chunks. Cannot proceed.", file=sys.stderr)
                 return [], [(1, total_lines)], full_compile_error


        good_ranges = []
        bad_ranges = []
        processed_lines = [False] * (total_lines + 1) # 1-indexed

        # Try to compile each identified AST chunk
        for chunk_content, (start_line, end_line) in chunks:
            if all(processed_lines[start_line : end_line+1]): # Already covered by a larger good chunk
                continue

            # Prepend necessary headers/metadata if the chunk is LaTeX, etc.
            # For generic markdown-to-pdf, often not needed unless there are document-level settings.
            # For now, assume chunks are relatively self-contained or pandoc handles fragments.
            # A more advanced version might need to add `--- \n ... \n ---` or LaTeX preamble.

            # If a chunk is very small (e.g., one line of text), compiling it alone might fail
            # if it relies on context (e.g., inside a list). Pandoc is sometimes robust.
            # The goal is to find *minimal* compilable pieces.
            # And *minimal* non-compilable pieces.

            success, error = compile_markdown_to_pdf(chunk_content, temp_pdf_file)
            # No need to rm temp_pdf_file here, it's handled in the finally block for the whole function call

            if success:
                good_ranges.append((start_line, end_line))
                for i in range(start_line, end_line + 1):
                    processed_lines[i] = True
            else:
                # This chunk is bad. We could try to recursively break it down.
                # For now, mark it as a bad range.
                # The problem states: "You may consider trying to intelligently break
                # non-compilable line ranges into even smaller sub-ranges"

                # If the chunk is small enough (e.g. 1-3 lines), don't break down further.
                if (end_line - start_line + 1) <= 3 : # Arbitrary threshold
                     bad_ranges.append((start_line, end_line))
                else:
                    # Try to split this failing chunk further using line-based splitting
                    # as a simple recursive step. A more advanced step would re-run AST analysis
                    # on the chunk content, but that might be complex if the chunk is not valid standalone MD.
                    sub_chunks = split_markdown_by_lines(chunk_content, 1) # Split line by line

                    current_sub_bad_start = -1
                    for i, (sub_chunk_content, (original_sub_start, original_sub_end)) in enumerate(sub_chunks):
                        actual_start_line = start_line + original_sub_start - 1
                        actual_end_line = start_line + original_sub_end - 1

                        sub_success, _ = compile_markdown_to_pdf(sub_chunk_content, temp_pdf_file)
                        # temp_pdf_file cleaned in finally

                        if not sub_success:
                            if current_sub_bad_start == -1:
                                current_sub_bad_start = actual_start_line
                            # If this is the last sub_chunk and it's bad, close the range
                            if i == len(sub_chunks) - 1:
                                bad_ranges.append((current_sub_bad_start, actual_end_line))
                        else: # sub_success is True
                            if current_sub_bad_start != -1:
                                # Previous sub-chunk was bad, and this one is good. Close the bad range.
                                bad_ranges.append((current_sub_bad_start, actual_start_line -1))
                                current_sub_bad_start = -1
                            good_ranges.append((actual_start_line, actual_end_line)) # This part of the larger bad chunk is good

                    # If the loop finished and there was an open bad range (e.g. last line was bad)
                    if current_sub_bad_start != -1 and current_sub_bad_start <= end_line : # ensure it's within original failing chunk
                         # The end of this sub-bad-range should be the end of the parent failing chunk
                         # if all subsequent lines also failed.
                         # This logic is a bit tricky; it should be the last failing line.
                         # The current logic appends up to actual_start_line -1 for the last good one,
                         # or actual_end_line for the last bad one.
                         # If the loop ends and current_sub_bad_start is set, it means the last line(s) were bad.
                         # The range should go up to end_line (the end of the parent chunk).
                         # This is implicitly handled if the last sub_chunk is bad.
                         pass


        # Consolidate overlapping/adjacent ranges
        good_ranges = _consolidate_ranges(sorted(good_ranges))
        bad_ranges = _consolidate_ranges(sorted(bad_ranges))

        # Identify lines not covered by any "good" AST-based chunk as potentially problematic
        # This is a simpler way than complex recursion for now.
        # The initial `bad_ranges` from direct AST chunk failures are a starting point.
        # We need to find all lines that are NOT in good_ranges.

        final_bad_ranges = []
        if not good_ranges and not bad_ranges and not full_compile_success: # No good chunks found, whole doc is bad
            return [], [(1, total_lines)], full_compile_error

        if not good_ranges and bad_ranges: # Only bad chunks found (e.g. from recursive step)
            return [], _consolidate_ranges(sorted(bad_ranges)), full_compile_error

        # If there are good_ranges, infer bad_ranges from the gaps
        if good_ranges:
            # Infer bad ranges from gaps in good_ranges
            # This assumes that if a line isn't in a good_range, it's part of a bad_range.
            # This is a strong assumption if AST splitting was coarse.
            # The `bad_ranges` collected from direct failures of chunks is more precise.
            # Let's combine them.

            current_line = 1
            inferred_bad_ranges = []
            for start_good, end_good in good_ranges:
                if current_line < start_good:
                    inferred_bad_ranges.append((current_line, start_good - 1))
                current_line = end_good + 1
            if current_line <= total_lines:
                inferred_bad_ranges.append((current_line, total_lines))

            # Combine inferred bad ranges with directly identified bad ranges
            combined_bad_ranges = _consolidate_ranges(sorted(bad_ranges + inferred_bad_ranges))
            final_bad_ranges = combined_bad_ranges
        else: # No good ranges, means the whole document is essentially bad, or AST splitting was ineffective
            final_bad_ranges = [(1, total_lines)] if not bad_ranges else _consolidate_ranges(sorted(bad_ranges))

        return good_ranges, final_bad_ranges, full_compile_error

    finally:
        if temp_pdf_file and os.path.exists(temp_pdf_file):
            try:
                os.remove(temp_pdf_file)
            except OSError as e:
                # Non-critical, but good to know if cleanup fails
                print(f"Warning: Could not remove temporary file {temp_pdf_file}: {e}", file=sys.stderr)


def _consolidate_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Consolidates overlapping or adjacent line ranges."""
    if not ranges:
        return []

    # Sort by start line, then by end line
    ranges.sort(key=lambda x: (x[0], x[1]))

    merged = []
    for current_start, current_end in ranges:
        if not merged or current_start > merged[-1][1] + 1:
            # No overlap and not adjacent: start a new merged range
            merged.append((current_start, current_end))
        else:
            # Overlap or adjacent: merge with the last one
            merged[-1] = (merged[-1][0], max(merged[-1][1], current_end))
    return merged


if __name__ == '__main__':
    # Example Usage (for testing purposes)
    test_md_valid = """
# Valid Markdown

This is a simple valid markdown document.

- Item 1
- Item 2
"""
    test_md_invalid_latex = """
# Invalid LaTeX Test

This document has a LaTeX error.

\\begin{enumerate}
  \\item Item one
  \\item Item two
\\end{enumerate}

But then, an unclosed LaTeX environment:
\\begin{itemize} % Line 10
  \\item Bad item
% Missing \\end{itemize}
""" # Error expected around line 10-12

    test_md_simple_error = """
# Simple Error

This has an undefined command: \\myundefinedcommand % Line 3
""" # Error expected at line 3

    test_md_middle_error = """
Line 1 is fine.
Line 2 is fine.
\\erroreouscommand % Line 3
Line 4 is fine.
Line 5 is fine.
""" # Error at line 3

    test_md_multiple_errors = """
Valid start. % Line 1

\\badcommandone % Line 3

Valid middle.

\\anotherbadcommand % Line 7

Valid end.
""" # Errors at 3 and 7


    print("--- Testing valid markdown ---")
    good, bad, err = find_error_ranges(test_md_valid)
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}")
    if err: print(f"  Initial error: {err[:100]}...") # Print snippet of error

    print("\n--- Testing invalid LaTeX markdown ---")
    good, bad, err = find_error_ranges(test_md_invalid_latex)
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}") # Expected: something around line 10
    if err: print(f"  Initial error: {err.splitlines()[0] if err else ''}")

    print("\n--- Testing simple error markdown ---")
    good, bad, err = find_error_ranges(test_md_simple_error)
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}") # Expected: (3,3)
    if err: print(f"  Initial error: {err.splitlines()[0] if err else ''}")

    print("\n--- Testing middle error markdown ---")
    good, bad, err = find_error_ranges(test_md_middle_error)
    print(f"  Good ranges: {good}") # Expected: [(1,2), (4,5)]
    print(f"  Bad ranges: {bad}")   # Expected: [(3,3)]
    if err: print(f"  Initial error: {err.splitlines()[0] if err else ''}")

    print("\n--- Testing multiple errors markdown ---")
    good, bad, err = find_error_ranges(test_md_multiple_errors)
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}") # Expected: [(3,3), (7,7)] or similar
    if err: print(f"  Initial error: {err.splitlines()[0] if err else ''}")

    # Test case where AST splitting might be problematic or coarse
    test_md_subtle_block_error = """
\\documentclass{article}
\\begin{document}

This is a paragraph.

\\begin{itemize}
    \\item Item 1
    \\item Item 2 \\errorhere % Error inside a block
\\end{itemize}

Another paragraph.

\\end{document}
"""
    print("\n--- Testing subtle block error markdown ---")
    # This requires pandoc to process it as LaTeX directly, or use a LaTeX template.
    # The default markdown -> pdf might not catch this well if \\errorhere is not a md error.
    # If we assume it's markdown with embedded LaTeX.
    # `compile_markdown_to_pdf` might need `-f markdown+raw_tex`
    # For now, `compile_markdown_to_pdf` is simple.
    # Let's assume `\\errorhere` causes a pdflatex failure.
    good, bad, err = find_error_ranges(test_md_subtle_block_error)
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}")
    if err: print(f"  Initial error: {err.splitlines()[0] if err else ''}")

    # Test with an empty file
    print("\n--- Testing empty markdown ---")
    good, bad, err = find_error_ranges("")
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}")
    if err: print(f"  Initial error: {err}")

    # Test with a file that's entirely one error
    test_md_all_error = "\\completelybroken"
    print("\n--- Testing markdown that is entirely an error ---")
    good, bad, err = find_error_ranges(test_md_all_error)
    print(f"  Good ranges: {good}")
    print(f"  Bad ranges: {bad}")
    if err: print(f"  Initial error: {err.splitlines()[0] if err else ''}")
