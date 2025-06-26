import pytest
from PySide6.QtWidgets import QApplication
from src.main import MainWindow # Assuming src is in PYTHONPATH or tests are run from root

# Fixture to create a QApplication instance for tests that need it
@pytest.fixture(scope="session")
def qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.mark.smoke
def test_main_window_creation(qt_app, qtbot):
    """Test if the MainWindow can be created and loads default content."""
    window = MainWindow()
    qtbot.addWidget(window) # Register window with qtbot for cleanup and interaction
    assert window is not None
    # Default title after load_default_content() call in init
    assert window.windowTitle() == "Pandoc Typora V2 - Untitled (Default)"
    window.show() # Needed for some widgets to initialize properly
    assert window.isVisible()

    # Check if editor has content from default.md
    assert "# Markdown Torture Test" in window.editor.toPlainText()
    assert not window.editor.document().isModified() # Should not be modified initially

    window.close() # Close the window

@pytest.mark.smoke
def test_main_window_editor_exists_and_has_default_content(qt_app, qtbot):
    """Test if the editor widget exists and has default content loaded."""
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.editor is not None
    assert "# Markdown Torture Test" in window.editor.toPlainText()
    window.close()

@pytest.mark.smoke
def test_main_window_preview_widget_exists(qt_app, qtbot):
    """Test if the preview widget (in the dock) exists."""
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.preview_widget is not None
    assert window.preview_dock.widget() == window.preview_widget
    window.close()

# TODO: Add more tests for:
# - Menu actions triggering corresponding methods (e.g., file_new, file_open)
# - Dock widget visibility toggles
# - Initial state of various UI elements
# - File operations (mocking QFileDialog)
# - Unsaved changes dialog (later sprint)
