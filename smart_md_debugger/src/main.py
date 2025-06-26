#!/usr/bin/env python3
import sys
import os
import shutil # For checking pandoc availability

# Adjust import path to correctly find debugger and splitter
# This assumes main.py is in smart_md_debugger/src and debugger/splitter are in the same directory
try:
    from debugger import find_error_ranges
    from linter import lint_markdown, LinterError # Import linter components
except ImportError:
    # If running from the root of the project (e.g. python src/main.py)
    # then src needs to be in pythonpath or use relative imports from a package.
    # For a simple script structure, this might mean src is the current working directory
    # or we adjust sys.path.
    # Assuming execution from within `src` or `smart_md_debugger` directory where `src` is a package.
    # If 'smart_md_debugger' is the top-level package and 'src' is a sub-package/module:
    # from ..src.debugger import find_error_ranges # If main was outside src
    # If src is the root for modules:
    from debugger import find_error_ranges
    from linter import lint_markdown, LinterError


def print_linter_errors(errors: list[LinterError]):
    """Prints linter errors to stderr."""
    if errors:
        print("--- Linter Pre-check Found Issues ---", file=sys.stderr)
        for line_num, err_type, msg, sugg in errors:
            suggestion_text = f" Suggestion: {sugg}" if sugg else ""
            print(f"  Linter [Line {line_num} ({err_type})]: {msg}{suggestion_text}", file=sys.stderr)
        print("--- Continuing with Pandoc Debugging ---", file=sys.stderr)
    else:
        print("--- Linter Pre-check Passed (No obvious issues found) ---", file=sys.stderr)


def main():
    """
    Main function for the smart markdown debugger CLI.
    Reads markdown from stdin, processes it, and prints results.
    """
    if not sys.stdin.isatty():
        markdown_input = sys.stdin.read()
    else:
        print("No input provided via stdin. Pipe markdown content into the script.", file=sys.stderr)
        print("Usage: pandoc_debug < markdown_file.md", file=sys.stderr)
        sys.exit(1)

    if not markdown_input.strip():
        print("Input is empty.", file=sys.stderr) # Output to stderr as it's a status message
        sys.exit(0) # Not an error, just nothing to do.

    # Check for pandoc availability early
    if shutil.which("pandoc") is None:
        print("Error: pandoc command not found. Please ensure pandoc is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)

    # Run Linter Pre-check
    linter_errors = lint_markdown(markdown_input)
    print_linter_errors(linter_errors)

    # Proceed with Pandoc-based debugging
    print("\nStarting Pandoc-based analysis...\n", file=sys.stderr) # Progress message to stderr
    good_ranges, bad_ranges, initial_error = find_error_ranges(markdown_input)

    if not bad_ranges and good_ranges:
        # Check if the entire document was good
        if len(good_ranges) == 1 and good_ranges[0][0] == 1:
            total_lines = len(markdown_input.splitlines())
            if good_ranges[0][1] == total_lines:
                print("Markdown compiled successfully!", file=sys.stderr)
                print("\nNo errors found.")
                return # Exit successfully

    if initial_error and not bad_ranges and not good_ranges : # e.g. AST parsing failed
        print("An critical error occurred during initial processing:", file=sys.stderr)
        print(initial_error, file=sys.stderr)
        if not bad_ranges: # If find_error_ranges couldn't pinpoint, it might return a full range.
             total_lines = len(markdown_input.splitlines())
             print(f"\nSuspected problematic line range(s) (could be the whole document):")
             print(f"  Lines 1-{total_lines}") # Default to whole document if nothing specific
        sys.exit(1)


    if bad_ranges:
        print("Found potential problematic line range(s):")
        for start, end in bad_ranges:
            print(f"  Lines {start}-{end}")

        if initial_error:
            print("\nInitial pandoc error message (when compiling the whole document):", file=sys.stderr)
            # Limit the length of the error message printed
            error_lines = initial_error.splitlines()
            for i, line in enumerate(error_lines):
                if i < 10: # Print first 10 lines of error
                    print(f"  {line}", file=sys.stderr)
                elif i == 10:
                    print(f"  ... (error message truncated)", file=sys.stderr)
                    break
    elif not good_ranges and not initial_error:
         print("Could not determine specific error ranges, but the document failed to compile.", file=sys.stderr)
         print("The error might be global or related to document structure not capturable by AST blocks.", file=sys.stderr)
    else: # No bad ranges, but not the "whole document is good" case (e.g. empty input handled earlier)
        # This case should ideally be covered by the "Markdown compiled successfully!"
        # Or if it's an unexpected state.
        print("No specific problematic ranges identified, but the document might have issues if it didn't fully compile.", file=sys.stderr)
        if initial_error:
             print("\nInitial pandoc error (whole document):", file=sys.stderr)
             print(initial_error, file=sys.stderr)

    # Temporary file cleanup is now handled within find_error_ranges's finally block.

if __name__ == "__main__":
    main()
