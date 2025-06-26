# Pandoc Typora V2 - Roadmap

This document outlines the development roadmap for Pandoc Typora V2, a Markdown editor focused on Pandoc integration and a touch-friendly UI.

## Core Philosophy

- **MVP First:** Achieve a usable core product quickly.
- **Pandoc-Centric:** Leverage Pandoc's strengths for Markdown processing and extensions.
- **Thesis-Focused:** Prioritize features beneficial for long-form academic writing.
- **Modern & Touch-Friendly:** Utilize PySide6 for a contemporary UI suitable for hybrid devices.
- **Iterative Sprints:** Develop in hackathon-style sprints to make significant progress.

## Current State (MVP Achieved)

- [x] Basic PySide6 application window with menu, toolbar, status bar.
- [x] Core Markdown text editor (`QTextEdit`).
- [x] Basic syntax highlighting for Markdown.
- [x] Live preview panel using Pandoc (via `QProcess`).
    - [x] Updates on text change (debounced).
    - [x] Supports common Pandoc extensions (fenced_divs, footnotes, etc. via arguments).
- [x] Basic file operations: New, Open, Save, Save As.
- [x] Dockable panels for File/Settings (placeholder cards) and Preview.
- [x] View menu toggles for panels.

## Sprint Plan

The development will proceed in a series of sprints, each focusing on a set of features.

---

### Sprint 1: "Polishing the Core & Usability" (MVP+1)

**Goal:** Enhance the existing MVP for a smoother user experience and lay groundwork for advanced features.

**Features:**

- **Editor Enhancements:**
    - [ ] **Unsaved Changes Handling:** Prompt user to save on New, Open, Exit if changes are unsaved. Implement `closeEvent` for the main window.
    - [ ] **Improved Syntax Highlighting:**
        - [ ] More robust handling of nested Markdown structures.
        - [ ] Configurable themes/colors for syntax highlighting.
        - [ ] Highlight matching Markdown pairs (e.g., `*_*`, `(**)`).
    - [ ] **Basic Auto-indentation** and smart list continuation.
    - [ ] **Spell Checking** (platform-dependent or via library).
- **Preview Enhancements:**
    - [ ] **CSS Styling for Preview:** Allow custom CSS for the Pandoc HTML preview for better visual parity with final output and support for styled blocks (fenced divs).
        - [ ] Default stylesheet for common elements (headers, blockquotes, code).
        - [ ] Mechanism to load user-defined CSS.
    - [ ] **Scroll Sync:** Attempt basic synchronization between editor and preview scroll positions.
- **UI & UX:**
    - [ ] **File Browser Card Implementation:**
        - [ ] Basic tree view for a directory.
        - [ ] Open files from tree view.
        - [ ] Set a root "project" directory.
    - [ ] **Settings Card Implementation (Basic):**
        - [ ] Option to set Pandoc executable path.
        - [ ] Option to select/manage preview CSS.
    - [ ] **Toolbar Customization:** Add common actions (Bold, Italic, Code, etc.) to the toolbar.
    - [ ] **Recent Files Menu:** Implement a "File > Open Recent" menu.
- **Stability & Testing:**
    - [ ] **Unit Tests:** Expand unit tests for core components (file operations, Pandoc interaction).

---

### Sprint 2: "Academic Power Tools"

**Goal:** Introduce features critical for thesis and long-form academic writing.

**Features:**

- **Pandoc Integration Deep Dive:**
    - [ ] **Citation Management (CSL & Bibliography):**
        - [ ] UI to specify bibliography files and CSL style.
        - [ ] Auto-update preview with resolved citations.
        - [ ] Helper for inserting citation keys (e.g., `@key`).
    - [ ] **Cross-Referencing:** Ensure Pandoc's cross-referencing syntax (`@label`) works and is previewable.
    - [ ] **Table of Contents Generation:**
        - [ ] Option to generate and display ToC in preview (or separate panel).
        - [ ] `--toc` and `--toc-depth` Pandoc options.
    - [ ] **Equation Numbering & Referencing:** For LaTeX math.
- **Editor Features for Long Documents:**
    - [ ] **Outline View/Document Map:** A panel showing document structure based on headers.
    - [ ] **Word Count & Statistics:** Display in status bar or a dedicated panel.
    - [ ] **Focus Mode / Typewriter Mode:** Options to enhance writing focus.
- **Export Options:**
    - [ ] **Advanced Export Dialog:**
        - [ ] Select output format (HTML, PDF, DOCX, LaTeX, etc.).
        - [ ] Specify Pandoc command-line arguments.
        - [ ] Template selection (`--template` option).
        - [ ] Variable passing (`-V key=val`).
    - [ ] Direct PDF export (via LaTeX/WeasyPrint/Typst as configured in Pandoc).

---

### Sprint 3: "Advanced Editing & Customization"

**Goal:** Refine the editor with more advanced features and allow greater user customization.

**Features:**

- **Advanced Editor Features:**
    - [ ] **Smart Editing Helpers:**
        - [ ] Auto-pairing of brackets, quotes.
        - [ ] Smart table editing assistance.
    - [ ] **Find & Replace:** Robust find/replace in editor.
    - [ ] **Multiple Document Interface (Tabs):** Allow multiple files to be open in tabs.
- **Pandoc Extensions & Filters:**
    - [ ] **Lua Filter Management:** UI to enable/disable/manage custom Pandoc Lua filters.
    - [ ] **Support for Custom Divs/Spans Styling:** Deeper integration for `::: div` and `[span]{.class}` styling in preview.
- **UI Customization:**
    - [ ] **Application Theming:** Light/Dark mode for the application itself.
    - [ ] **Font Customization:** For editor and UI.
    - [ ] **Layout Customization:** Allow users to rearrange/resize dock widgets more freely and save layouts.
- **Touch & Hybrid UI Polish:**
    - [ ] **Larger Touch Targets** for key UI elements (optional mode or adaptive).
    - [ ] **On-screen Keyboard Handling** improvements if issues are found.
    - [ ] **Gesture Support** (e.g., pinch-to-zoom in preview if feasible).

---

### Sprint 4: "Feature Parity & Beyond"

**Goal:** Approach feature parity with established editors and explore unique offerings.

**Features:**

- **Version Control (Git) Integration (Basic):**
    - [ ] Indicate modified files.
    - [ ] Basic commit/diff view (could be very minimal).
- **Session Management:**
    - [ ] Remember open files and panel layouts across sessions.
- **Plugin System (Ambitious):**
    - [ ] Define an API for extending functionality (e.g., new syntax highlighting, custom previewers).
- **Diagrams & Special Blocks:**
    - [ ] Integration with tools like Mermaid.js or PlantUML for diagram previews (if Pandoc filters allow).
- **Accessibility (A11y):**
    - [ ] Review and improve keyboard navigation.
    - [ ] Ensure screen reader compatibility where possible.

---

### Future Considerations / Backlog

- Cloud synchronization (Dropbox, Drive, etc.).
- Collaborative editing (very ambitious).
- More export formats and fine-grained control.
- Advanced project management features (beyond single files).
- Mobile version (would require significant framework changes, e.g., Kivy or web tech).

---

This roadmap is a living document and will be updated as the project progresses and user feedback is incorporated.Tool output for `create_file_with_block`:
