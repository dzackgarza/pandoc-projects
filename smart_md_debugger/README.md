# Smart Markdown Debugger

A command-line tool to help identify problematic line ranges in Markdown files that fail to compile to PDF using Pandoc.

## Purpose

When `pandoc` fails to convert a Markdown file to PDF, it often reports errors that can be difficult to trace back to the exact lines in the source Markdown, especially for complex documents or those with embedded LaTeX. This tool attempts to pinpoint the failing sections by:

1.  Parsing the Markdown into an Abstract Syntax Tree (AST) using Pandoc.
2.  Intelligently splitting the document into the smallest possible chunks based on AST blocks (e.g., paragraphs, code blocks, list items).
3.  Attempting to compile each chunk individually.
4.  Reporting the line ranges that successfully compile and, more importantly, the line ranges that fail.
5.  If an AST block fails, it may try to further break down that block line by line to narrow down the error.

This helps users quickly locate and fix errors in their Markdown source.

## Prerequisites

*   **Python 3.x**
*   **Pandoc**: Must be installed and accessible in your system's PATH. PDF generation via Pandoc typically requires a LaTeX distribution (like TeX Live, MiKTeX, or MacTeX).

## Usage

The tool reads Markdown content from standard input and prints the identified problematic line ranges to standard output. Error messages and progress are printed to standard error.

```bash
# Navigate to the src directory where main.py is located
cd path/to/smart_md_debugger/src

# Pipe a markdown file into the script
./main.py < ../tests/test_latex_error.md
```

Or, if `src` is in your `PYTHONPATH` or the tool is installed as a package (future step):
```bash
# Assuming main.py is runnable and in PATH or called via python -m smart_md_debugger.src.main
python path/to/smart_md_debugger/src/main.py < path/to/your_document.md
```

Example:
```bash
cat my_document.md | python path/to/smart_md_debugger/src/main.py
```

## Interpreting Output

The tool will output:
*   A list of "problematic line range(s)". These are the sections it identified as causing compilation failures.
*   The initial error message from Pandoc when attempting to compile the whole document (to `stderr`).

If the document compiles successfully, it will indicate that.

## Test Cases

The `tests/` directory contains several example Markdown files that can be used to test the debugger:

1.  **`test_latex_error.md`**
    *   **Error**: Contains an undefined LaTeX command (`\thiscommandisnotdefined`).
    *   **Expected Output**: Should identify the line containing the undefined command (around line 5).

2.  **`test_unclosed_env.md`**
    *   **Error**: An unclosed LaTeX `itemize` environment.
    *   **Expected Output**: Should identify the range where the `itemize` environment starts and isn't properly closed (around lines 5-7).

3.  **`test_malformed_table.md`**
    *   **Error**: A table with a comment that might break its structure. (Pandoc is often robust; actual failure depends on its LaTeX conversion of tables).
    *   **Expected Output**: If it fails, it should point to the table lines (around lines 5-8). If Pandoc handles it, it will compile.

4.  **`test_multiple_errors.md`**
    *   **Error**: Multiple errors: undefined LaTeX command, unclosed TikZ environment, invalid UTF character.
    *   **Expected Output**: Should identify multiple failing ranges corresponding to:
        *   Line with `\undefinedLaTeXcommandHere` (around line 5).
        *   The TikZ environment (around lines 12-14).
        *   The line with the invalid character `�` (around line 18).

5.  **`test_valid_document.md`**
    *   **Error**: None. This is a valid document.
    *   **Expected Output**: "Markdown compiled successfully!" or "No errors found."

### Running a Test Case:
```bash
# From the smart_md_debugger/src directory
./main.py < ../tests/test_latex_error.md
```

## How it Works

The tool operates in two main phases:

1.  **Linter Pre-check (Static Analysis):**
    *   Before attempting any Pandoc compilation, the input Markdown is first processed by a built-in linter.
    *   This linter performs static analysis to find common syntax and structural issues that often lead to LaTeX errors.
    *   **Checks Performed:**
        *   **Backtick Escaping:** Detects LaTeX commands (e.g., `` `\sum` ``, `` `\begin{env}` ``) incorrectly wrapped in single backticks.
        *   **Mismatched Math Delimiters:** Uses a stack-based approach to check for unclosed or mismatched math delimiters (`$`, `$$`, `\(`, `\)`, `\[`, `\]`). Also flags some suspicious mixing of types.
        *   **Mismatched Environment Delimiters:** Uses a stack-based approach for LaTeX environments (`\begin{...}`, `\end{...}`), checking for unclosed environments or mismatched `\end` tags.
        *   **Common LaTeX Command Issues:** Identifies potential problems like double subscripts/superscripts (e.g., `x_a_b`) and common commands (e.g., `\sqrt`, `\textbf`) used with multi-token arguments without braces.
    *   **Output:** Linter findings are printed to `stderr`, indicating the line number, error type, a descriptive message, and often a suggestion for a fix. Example:
        ```
        --- Linter Pre-check Found Issues ---
          Linter [Line 5 (BACKTICK_ESCAPING)]: LaTeX-like expression '\sum' found wrapped in single backticks: '`\sum`'. This will be treated as literal code. Suggestion: If '\sum' is intended as LaTeX, remove the backticks. If it's math, ensure it's also within $...$ or a math environment. E.g., change to '\sum' or '$\sum$'.
          Linter [Line 10 (UNCLOSED_ENV)]: Unclosed environment \begin{itemize} opened at line 10, col 0. Suggestion: Ensure it is properly closed with \end{itemize}.
        --- Continuing with Pandoc Debugging ---
        ```
    *   After the linter runs, the tool proceeds to the Pandoc-based debugging phase regardless of linter findings.

2.  **Pandoc-based Debugging (Dynamic Analysis):**
    *   **Full Compilation Attempt**: Tries to compile the entire document using Pandoc. If successful, it reports this and exits.
    *   **AST Generation**: If the full compilation fails, it uses `pandoc --sourcepos -t json` to get a structured representation (Abstract Syntax Tree) of the Markdown, including source position information for elements.
    *   **Chunking**: Splits the document into chunks. Priority is given to splitting based on identified AST blocks (respecting logical units like paragraphs, code blocks). If AST-based splitting is not effective (e.g., for very simple documents or if Pandoc doesn't provide detailed source positions for all blocks), it may fall back to line-by-line splitting.
    *   **Individual Chunk Compilation**: Each chunk is compiled separately using Pandoc:
        *   Successful chunks are marked as "good."
        *   Failed chunks are further analyzed:
            *   If the failing chunk is small (e.g., 1-3 lines), the whole chunk is marked "bad."
            *   If the failing chunk is larger, it's recursively split line-by-line, and each of these smaller lines is compiled to attempt to pinpoint the exact failing line(s) within that block.
    *   **Report Generation**: Consolidates all identified "good" and "bad" line ranges. The "bad" ranges (those that failed compilation and could not be successfully broken down further into compiling sub-parts) are printed to `stdout` as the suspected problematic areas. The initial error message from Pandoc (for the whole document) is also shown on `stderr` for context.

## Test Cases

The `tests/` directory contains several example Markdown files:

*   **For Pandoc Debugger:**
    *   `test_latex_error.md`: Undefined LaTeX command.
    *   `test_unclosed_env.md`: Unclosed LaTeX environment (will also be caught by linter).
    *   `test_malformed_table.md`: Potentially malformed Markdown table.
    *   `test_multiple_errors.md`: Various distinct errors.
    *   `test_valid_document.md`: Should compile without errors.

*   **For Linter Pre-check:**
    *   `test_linter_backticks.md`: Focuses on backtick escaping issues.
    *   `test_linter_math_delimiters.md`: Tests math delimiter pairings.
    *   `test_linter_env_delimiters.md`: Tests LaTeX environment pairings.
    *   `test_linter_commands.md`: Tests common command issues (double scripts, missing braces).
    *   `test_linter_mixed.md`: Contains a mix of various linter errors.
    *   `test_linter_clean.md`: Should pass all linter checks.

### Running a Test Case:
```bash
# From the smart_md_debugger/src directory
./main.py < ../tests/test_linter_backticks.md
# or
./main.py < ../tests/test_latex_error.md
```

## Limitations & Future Improvements

*   **Context Dependency**: Some Markdown/LaTeX errors only manifest with specific surrounding content or preamble. Compiling small chunks in isolation might not always reproduce the exact error or might introduce new ones (e.g., if a chunk relies on a macro defined elsewhere). The tool currently doesn't manage complex preambles for chunks.
*   **AST Splitting Granularity**: The effectiveness of `get_block_source_positions` in `splitter.py` depends on Pandoc providing detailed `sourcepos` attributes. Some complex or nested structures might not be split optimally.
*   **Performance**: For very large files, compiling many small chunks can be slow.
*   **Error Message Correlation**: While the initial global error is shown, linking specific chunk errors back to precise Pandoc error messages for those chunks could be improved.
*   **Setup as a Package**: Properly package the tool for easier installation and execution.
*   **Temporary File Handling**: Improve temporary file creation (e.g., using the `tempfile` module for unique names and safer handling). (DONE)

This tool provides a best-effort approach to error localization.

## ROADMAP & Vision for Advanced Document Debugging

This section outlines a vision for significant improvements to this application and explores broader ideas for intelligent document debugging.

### I. Enhancements for Smart Markdown Debugger

1.  **Context-Aware Chunk Compilation:**
    *   **Preamble Injection:** Allow users to specify a common preamble (e.g., LaTeX document class, packages, custom macros, YAML frontmatter for Pandoc) that gets prepended to each chunk before compilation. This would drastically improve accuracy for documents relying on such global definitions.
    *   **Automatic Preamble Detection:** Attempt to automatically identify and extract common preambles or document setup commands from the original Markdown/LaTeX.

2.  **More Sophisticated Splitting Algorithms:**
    *   **Recursive AST Analysis:** When an AST block fails, instead of just line-by-line, re-parse the *content* of that block with Pandoc to get a sub-AST (if possible) and perform a more structured recursive debug.
    *   **Semantic Boundary Recognition:** Improve identification of logical units that *must not* be split (e.g., LaTeX `\begin{...}...\end{...}` environments, Markdown tables spanning multiple lines, fenced code blocks with internal structure). This might involve more detailed AST traversal or regex-based pre-checks.
    *   **Cost-Benefit Analysis for Splitting:** Implement a strategy where the tool decides if further splitting of a failing chunk is likely to yield a more precise error location versus the computational cost. For example, if a 50-line chunk fails and it's a known "atomic" LaTeX environment, splitting it further might be pointless.

3.  **Interactive Debugging Mode:**
    *   Allow the user to step through chunks, see the content, and manually mark them as good/bad or suggest alternative split points.
    *   Visualize the document structure and highlighted error zones.

4.  **Error Pattern Recognition and Suggested Fixes:**
    *   **Knowledge Base of Common Errors:** Build a database of common Pandoc/LaTeX error messages and link them to typical Markdown causes and potential fixes.
    *   **Heuristic-Based Suggestions:** E.g., if "Undefined control sequence" error + suspected line contains `\somecommand`, suggest checking for typos or missing LaTeX packages.
    *   **Similarity Matching:** If a failing chunk is similar to a known problematic pattern, suggest related solutions.

5.  **Performance Optimization:**
    *   **Caching:** Cache compilation results for identical chunks.
    *   **Parallelization:** Explore compiling independent chunks in parallel (though Pandoc I/O might be a bottleneck).
    *   **Selective Recompilation:** If a small change is made, only recompile affected chunks.

6.  **Usability & Integration:**
    *   **GUI Interface:** A simple graphical interface for easier file selection and results visualization.
    *   **Editor Integration:** Plugins for popular editors (VS Code, Sublime Text, etc.) to run the debugger and highlight errors directly in the editor.
    *   **Better Error Reporting:** Link specific Pandoc error snippets more directly to the chunk that produced them.

### II. Broader Vision: Intelligent Algorithms for Document Debugging

Beyond this specific tool, here are some ideas for advanced document debugging across various formats:

1.  **Bidirectional Debugging / Delta Debugging on Document Structure:**
    *   Start with the whole document (fails) and an empty document (succeeds).
    *   Iteratively add/remove sections (paragraphs, chapters, AST nodes) from the original document, attempting to compile at each step. This is similar to how `git bisect` works for commits, but applied to document structure.
    *   The goal is to find a *minimal set of additions* to the empty document that reproduces the error, or a *minimal set of removals* from the full document that fixes it.
    *   This is related to the [Delta Debugging](https://en.wikipedia.org/wiki/Delta_Debugging) algorithm.

2.  **Probabilistic Error Localization:**
    *   Based on a corpus of known good/bad documents and their errors, train a model to predict the likelihood of an error given certain features (e.g., specific LaTeX commands, complex table structures, presence of unusual Unicode).
    *   When a new document fails, use the model to rank sections by their probability of containing the error.

3.  **Comparative Analysis with Known Good Versions:**
    *   If a document used to compile but now fails (e.g., after changes), perform a structural diff (not just text diff) between the versions.
    *   Focus debugging efforts on the changed sections and their immediate surroundings.
    *   This could use techniques similar to [GumTree](https://github.com/GumTreeDiff/gumtree) for code, but adapted for document ASTs.

4.  **Constraint-Based Debugging for Formats with Schemas (e.g., XML, complex LaTeX styles):**
    *   If a document format has a formal schema or strict structural rules (e.g., DocBook XML, or a LaTeX class with many custom environments and constraints).
    *   Validate chunks against the schema or rules *before* attempting full compilation.
    *   Use constraint solvers to identify inconsistencies.

5.  **Learning from User Corrections:**
    *   If the tool suggests a problematic area and the user fixes it, record the "before" and "after" state of that chunk and the type of error.
    *   Use this data to improve the error pattern recognition and suggested fixes (see I.4).

6.  **"Why is this so slow?" Debugging for Document Compilation:**
    *   Beyond just pass/fail, some documents compile correctly but are extremely slow.
    *   Adapt the chunking and compilation approach to identify sections that contribute disproportionately to the compilation time. This would involve timing each chunk's compilation.

These ideas move towards a more AI-driven and deeply analytical approach to understanding and resolving document compilation issues.
