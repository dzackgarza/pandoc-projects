# TODO & Future Milestones

This document outlines planned improvements and future feature milestones for the Smart Markdown Debugger. It's based on the ROADMAP section in `README.md`.

## I. Linter Enhancements

-   [ ] **Refine Linter Rules & Regexes:**
    -   Improve regex for "missing braces for commands" to better capture complex arguments (e.g., `\sqrt \alpha_1` should suggest `\sqrt{\alpha_1}`).
    -   Improve `\frac` checking (currently disabled) to detect `\frac 12` or `\frac \alpha\beta` and suggest bracing.
    -   Reduce false positives or improve suggestions for "Mixed Delimiters" if current heuristics are too aggressive.
    -   More accurately report line/column numbers for multi-line constructs or complex matches.
-   [ ] **Configuration for Linter:**
    -   Allow users to enable/disable specific linter checks.
    -   Allow users to customize lists (e.g., commands that need braces).
-   [ ] **More Linter Checks:**
    -   Detect accidental `\ ` (space command) in prose.
    -   Discourage `\\` for newlines in Markdown (outside specific LaTeX contexts).
    -   Heuristic checks for matrix/array/table alignment tab issues.

## II. Debugger (`find_error_ranges`) Enhancements

-   [ ] **Context-Aware Chunk Compilation:**
    -   [ ] Allow users to specify a common preamble (YAML, LaTeX) to be used for compiling chunks.
    -   [ ] Attempt to automatically detect and extract common preambles.
-   [ ] **More Sophisticated Splitting Algorithms:**
    -   [ ] Implement recursive AST analysis for failing chunks (re-parse chunk content with Pandoc).
    -   [ ] Improve semantic boundary recognition to avoid splitting critical units (e.g., complex LaTeX environments).
    -   [ ] Add cost-benefit analysis for deciding when to stop splitting a failing chunk.
-   [ ] **Performance Optimization:**
    -   [ ] Implement caching for compilation results of identical chunks.
    -   [ ] Explore parallelization for compiling independent chunks.

## III. Error Handling & Reporting

-   [ ] **Better Correlation of Pandoc Errors:** Link specific Pandoc error messages more directly to the minimal failing chunk that produced them, rather than just showing the initial global error.
-   [ ] **Error Pattern Recognition & Suggested Fixes (Advanced):**
    -   [ ] Build a knowledge base of common Pandoc/LaTeX error messages and link them to typical Markdown causes and potential fixes.
    -   [ ] Implement heuristic-based suggestions for common errors.

## IV. Usability & Integration

-   [ ] **Interactive Debugging Mode:**
    -   [ ] Allow users to step through chunks, see content, mark good/bad, or suggest split points.
    -   [ ] Visualize document structure and highlighted error zones.
-   [ ] **GUI Interface:** Develop a simple graphical user interface.
-   [ ] **Editor Integration:** Create plugins for popular editors (VS Code, Sublime Text, etc.).
-   [ ] **Output Formatting:** Option for JSON or other machine-readable output for identified errors/ranges.

## V. Project & Packaging

-   [ ] **Formal Test Suite:** Implement a proper test suite using a framework like `unittest` or `pytest` for both linter and debugger components.
-   [ ] **Setup as a Python Package:** Properly package the tool for easier installation via `pip` (e.g., using `setup.py` or `pyproject.toml`).
-   [ ] **Dependency Management:** If Python dependencies are added, manage them robustly.
-   [ ] **Documentation:** Continuously improve README, add usage examples, and potentially Sphinx-based documentation for more detailed explanations.

## VI. Advanced Debugging Algorithms (Long-term Vision)

-   [ ] **Delta Debugging on Document Structure:** Implement algorithms to find minimal failing document subsets.
-   [ ] **Probabilistic Error Localization (ML-based):** Research and implement models to predict error likelihood in sections.
-   [ ] **Comparative Analysis with Known Good Versions:** Structural diffing to focus on changed sections.
-   [ ] **"Why is this so slow?" Debugging:** Identify performance bottlenecks in Pandoc compilation.
-   [ ] **Learning from User Corrections:** System to allow the tool to learn from how users fix reported issues.
