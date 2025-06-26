# Changelog

## [Unreleased] - YYYY-MM-DD

### Added
- **Linter Pre-check Module (`src/linter.py`)**:
  - Performs static analysis on Markdown input before Pandoc processing.
  - Detects improperly backticked LaTeX commands (e.g., `` `\sum` `` instead of `\sum` or `$\sum$`).
  - Implements stack-based checking for mismatched or unclosed math delimiters (`$`, `$$`, `\(`, `\)`, `\[`, `\]`). Includes basic detection of suspicious mixing of delimiter types.
  - Implements stack-based checking for mismatched or unclosed LaTeX environments (`\begin{...}` and `\end{...}`).
  - Checks for common LaTeX command issues:
    - Potential double subscripts/superscripts (e.g., `x_a_b`, `y^c^d`).
    - Missing braces for arguments to common commands like `\sqrt`, `\textbf`, `\textit`, `\emph` when the argument is multi-token or complex.
- **Integration of Linter into `main.py`**:
  - Linter runs automatically before the Pandoc-based debugging.
  - Linter findings (errors and suggestions) are printed to `stderr`.
- **New Linter-Specific Test Files**:
  - Added `test_linter_backticks.md`, `test_linter_math_delimiters.md`, `test_linter_env_delimiters.md`, `test_linter_commands.md`, `test_linter_mixed.md`, and `test_linter_clean.md` to the `tests/` directory.
- **README Updates**:
  - Updated "How it Works" section to detail the new two-phase process (Linter Pre-check, Pandoc-based Debugging).
  - Updated "Test Cases" section to include new linter-specific test files.
- **`TODO.md`**: Added a file outlining future development milestones.
- **`CHANGELOG.md`**: This file, to track changes.

### Fixed
- Resolved various `SyntaxWarning` issues in `linter.py` related to escape sequences in docstrings and test strings by using raw strings or correctly escaping backslashes.
- Corrected logic for `$$` handling in math delimiter checking to treat it as a toggle, improving accuracy for display math.
- Improved robustness of `find_error_ranges` in `debugger.py` by using `tempfile.NamedTemporaryFile` for pandoc outputs and ensuring cleanup.
- Added a fallback in `debugger.py` to line-based splitting if AST-based splitting yields no chunks.
- Added an explicit check for Pandoc availability at the start of `main.py`.

### Changed
- The `find_error_ranges` function in `debugger.py` no longer takes a `temp_pdf_path` argument, as it now manages its own temporary files.
- `main.py` updated to reflect changes in `find_error_ranges` signature.
- Minor refinements to error messages and suggestions from the linter.
