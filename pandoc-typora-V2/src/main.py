# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QMenuBar, QToolBar, QStatusBar, QDockWidget, QStackedWidget, QFileDialog
from PySide6.QtCore import Qt, QProcess, QTimer, QFile, QTextStream, QStandardPaths, QDir
from PySide6.QtGui import QAction
import pathlib # For path manipulation

# Import custom widgets
from widgets import FileBrowserCard, SettingsCard
from syntax_highlighter import MarkdownSyntaxHighlighter # Import the highlighter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pandoc Typora V2")
        self.setGeometry(100, 100, 1200, 800)

        self.current_file_path = None # To store the path of the currently open file
        self.pandoc_process = None # For running Pandoc
        self.pandoc_path = "pandoc" # TODO: Make this configurable

        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()
        self._create_dock_widgets()

        self.editor = QTextEdit()
        self.highlighter = MarkdownSyntaxHighlighter(self.editor.document())
        self.editor.textChanged.connect(self.schedule_pandoc_update)

        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(500) # ms delay before updating preview
        self.update_timer.timeout.connect(self.run_pandoc_conversion)

        self.main_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)

        self.load_default_content() # Load default content on startup


    def _create_menus(self):
        self.menu_bar = self.menuBar()

        # File Menu
        file_menu = self.menu_bar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.triggered.connect(self.file_new)
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.file_open)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.file_save)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self.file_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = self.menu_bar.addMenu("&Edit")
        # ... add edit actions

        # View Menu
        view_menu = self.menu_bar.addMenu("&View")

        toggle_file_settings_action = QAction("Toggle File/Settings Panel", self)
        toggle_file_settings_action.setCheckable(True)
        toggle_file_settings_action.setChecked(True) # Start visible
        toggle_file_settings_action.triggered.connect(self._toggle_file_settings_dock)
        view_menu.addAction(toggle_file_settings_action)

        toggle_preview_action = QAction("Toggle Preview Panel", self)
        toggle_preview_action.setCheckable(True)
        toggle_preview_action.setChecked(True) # Start visible
        toggle_preview_action.triggered.connect(self._toggle_preview_dock)
        view_menu.addAction(toggle_preview_action)

        # Help Menu
        help_menu = self.menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        help_menu.addAction(about_action)

    def _create_toolbars(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        # Example action
        # new_action_toolbar = QAction("New", self)
        # self.toolbar.addAction(new_action_toolbar)
        # ... add more toolbar actions

    def _create_statusbar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready", 3000)

    def _create_dock_widgets(self):
        # File Browser/Settings Card UI (Using custom Card widgets)
        self.file_settings_dock = QDockWidget("Files & Settings", self)
        self.file_settings_dock.setObjectName("FileSettingsDock")
        self.file_settings_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.card_stack_widget = QStackedWidget() # Renamed for clarity
        self.file_browser_card_instance = FileBrowserCard() # Instantiated custom card
        self.settings_card_instance = SettingsCard()     # Instantiated custom card

        self.card_stack_widget.addWidget(self.file_browser_card_instance)
        self.card_stack_widget.addWidget(self.settings_card_instance)

        # TODO: Add UI elements (e.g., buttons in a toolbar within the dock, or a tab bar)
        # to switch between cards in self.card_stack_widget.
        # For now, the first card added (FileBrowserCard) will be visible.

        self.file_settings_dock.setWidget(self.card_stack_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_settings_dock)

        # Pandoc Preview Dock
        self.preview_dock = QDockWidget("Pandoc Preview", self)
        self.preview_dock.setObjectName("PandocPreviewDock")
        self.preview_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.preview_widget = QTextEdit()
        self.preview_widget.setReadOnly(True)
        self.preview_dock.setWidget(self.preview_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.preview_dock)

    def schedule_pandoc_update(self):
        """Schedules a Pandoc update, resetting the timer if already active."""
        self.update_timer.start()

    def run_pandoc_conversion(self):
        if self.pandoc_process and self.pandoc_process.state() == QProcess.Running:
            # print("Pandoc is already running. Killing previous instance.")
            self.pandoc_process.kill() # Kill if it's taking too long
            self.pandoc_process.waitForFinished(100) # Wait a bit

        self.pandoc_process = QProcess(self)
        self.pandoc_process.setProcessChannelMode(QProcess.MergedChannels)
        self.pandoc_process.finished.connect(self._on_pandoc_finished)
        self.pandoc_process.errorOccurred.connect(self._on_pandoc_error)

        markdown_text = self.editor.toPlainText()
        if not markdown_text.strip():
            self.preview_widget.setHtml("") # Clear preview if no text
            return

        # Pandoc arguments: from markdown (with extensions) to HTML
        # CommonMark strict can be enabled with +commonmark_x if needed, but default Pandoc Markdown is fine.
        # For fenced divs: +fenced_divs or rely on it being default in newer Pandoc.
        # For styled blocks, we might need a custom Lua filter later if CSS isn't enough.
        args = [
            "-f", "markdown+footnotes+definition_lists+tex_math_dollars+fenced_divs+bracketed_spans", # Example extensions
            "-t", "html",
            "--standalone" # Include HTML header/footer for better rendering in QTextEdit
        ]

        # print(f"Running Pandoc with: {self.pandoc_path} {args}")
        self.pandoc_process.start(self.pandoc_path, args)
        self.pandoc_process.write(markdown_text.encode('utf-8'))
        self.pandoc_process.closeWriteChannel()

    def _on_pandoc_finished(self):
        if self.pandoc_process.exitStatus() == QProcess.NormalExit and self.pandoc_process.exitCode() == 0:
            html_output = self.pandoc_process.readAllStandardOutput().data().decode('utf-8')
            self.preview_widget.setHtml(html_output)
            # print("Pandoc conversion successful.")
        else:
            error_output = self.pandoc_process.readAllStandardError().data().decode('utf-8')
            if not error_output: # Sometimes output is on stdout for errors too
                 error_output = self.pandoc_process.readAllStandardOutput().data().decode('utf-8')
            self.preview_widget.setPlaceholderText(f"Pandoc Error (Exit Code: {self.pandoc_process.exitCode()}):\n{error_output}")
            print(f"Pandoc Error (Exit Code: {self.pandoc_process.exitCode()}):\n{error_output}")
        self.pandoc_process = None


    def _on_pandoc_error(self, error):
        error_string = self.pandoc_process.errorString()
        self.preview_widget.setPlaceholderText(f"Pandoc Execution Error: {error_string}")
        print(f"Pandoc Execution Error: {error_string}")
        # self.pandoc_process = None # Might be set to None by finished signal too

    # Methods to toggle dock visibility
    def _toggle_file_settings_dock(self):
        self.file_settings_dock.setVisible(not self.file_settings_dock.isVisible())

    def _toggle_preview_dock(self):
        self.preview_dock.setVisible(not self.preview_dock.isVisible())

    # --- File Operations ---
    def load_default_content(self):
        """Loads content from resources/default.md into the editor."""
        try:
            # Construct path to resources/default.md relative to main.py's directory
            # Assumes main.py is in src/ and resources/ is a sibling to src/
            # For robustness, it's better if resources are found relative to the app's execution path or installed location.
            # For now, let's assume a structure where pandoc-typora-V2 is the root.

            # Path to the directory containing this script (src)
            script_dir = pathlib.Path(__file__).parent
            # Path to the project root (pandoc-typora-V2)
            project_root = script_dir.parent
            default_md_path = project_root / "resources" / "default.md"

            if default_md_path.exists():
                file = QFile(str(default_md_path))
                if file.open(QFile.ReadOnly | QFile.Text):
                    stream = QTextStream(file)
                    self.editor.setPlainText(stream.readAll())
                    file.close()
                    self.current_file_path = None # Default content is not "saved" yet
                    self.setWindowTitle("Pandoc Typora V2 - Untitled (Default)")
                    self.statusbar.showMessage("Loaded default torture test document.", 3000)
                    self.editor.document().setModified(False) # Default content is not "modified" initially
                    self.schedule_pandoc_update()
                else:
                    self.statusbar.showMessage(f"Could not open default.md: {file.errorString()}", 5000)
                    self.editor.setPlainText("# Welcome to Pandoc Typora V2\n\nCould not load default.md.")
            else:
                self.statusbar.showMessage("default.md not found in resources.", 5000)
                self.editor.setPlainText("# Welcome to Pandoc Typora V2\n\nDefault content (default.md) not found.")
        except Exception as e:
            self.statusbar.showMessage(f"Error loading default.md: {e}", 5000)
            self.editor.setPlainText(f"# Welcome to Pandoc Typora V2\n\nError loading default.md: {e}")
        self.editor.moveCursor(self.editor.textCursor().Start) # Move cursor to start


    def file_new(self):
        # TODO: Check for unsaved changes before clearing
        self.load_default_content() # New file now loads the default torture test
        # self.editor.clear() # No longer just clearing
        # self.preview_widget.clear() # Done by load_default_content via schedule_pandoc_update
        # self.current_file_path = None # Done by load_default_content
        # self.setWindowTitle("Pandoc Typora V2 - Untitled") # Done by load_default_content
        self.statusbar.showMessage("New file (loaded default content).", 3000)


    def file_open(self):
        # TODO: Check for unsaved changes
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            documents_path,
            "Markdown Files (*.md *.markdown *.txt);;All Files (*)"
        )
        if file_path:
            try:
                file = QFile(file_path)
                if file.open(QFile.ReadOnly | QFile.Text):
                    stream = QTextStream(file)
                    self.editor.setPlainText(stream.readAll())
                    file.close()
                    self.current_file_path = file_path
                    self.setWindowTitle(f"Pandoc Typora V2 - {file_path}")
                    self.statusbar.showMessage(f"Opened {file_path}", 3000)
                    self.schedule_pandoc_update() # Update preview
                else:
                    self.statusbar.showMessage(f"Error opening file: {file.errorString()}", 5000)
            except Exception as e:
                self.statusbar.showMessage(f"Could not open file: {e}", 5000)

    def file_save(self):
        if self.current_file_path:
            try:
                file = QFile(self.current_file_path)
                if file.open(QFile.WriteOnly | QFile.Text | QFile.Truncate):
                    stream = QTextStream(file)
                    stream << self.editor.toPlainText()
                    file.close()
                    self.setWindowTitle(f"Pandoc Typora V2 - {self.current_file_path}")
                    self.statusbar.showMessage(f"Saved to {self.current_file_path}", 3000)
                else:
                    self.statusbar.showMessage(f"Error saving file: {file.errorString()}", 5000)
            except Exception as e:
                self.statusbar.showMessage(f"Could not save file: {e}", 5000)
        else:
            self.file_save_as() # If no current path, then "Save As"

    def file_save_as(self):
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        default_filename = "untitled.md"
        if self.current_file_path:
            # Suggest current filename if available
            from pathlib import Path
            default_filename = Path(self.current_file_path).name

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File As",
            documents_path + "/" + default_filename,
            "Markdown Files (*.md *.markdown *.txt);;All Files (*)"
        )
        if file_path:
            self.current_file_path = file_path # Update current path
            self.file_save() # Call regular save to write content

    # TODO: Add a closeEvent handler to check for unsaved changes before exiting.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
