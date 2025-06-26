import pytest
from PySide6.QtCore import QCoreApplication, QTimer # QCoreApplication for event loop in non-GUI tests
from PySide6.QtTest import QSignalSpy
from unittest.mock import patch, MagicMock

# Assuming src.main.MainWindow is where pandoc logic resides
# For this test, we might not need a full MainWindow instance if we can isolate
# the Pandoc calling mechanism. If it's tightly coupled, we use qtbot.
# For now, let's assume we can test parts of it or mock the QProcess.

# If MainWindow is necessary:
from src.main import MainWindow

@pytest.fixture
def app_instance():
    """Ensure a QCoreApplication instance exists for QProcess tests if not using qtbot."""
    if QCoreApplication.instance() is None:
        return QCoreApplication([])
    return QCoreApplication.instance()

@pytest.fixture
def main_window_mocked_pandoc(qtbot, qt_app): # qt_app from conftest or test_main_window
    """Provides a MainWindow instance with a mocked QProcess for Pandoc."""
    with patch('PySide6.QtCore.QProcess') as mock_qprocess_class:
        # Configure the instance returned by QProcess()
        mock_process_instance = MagicMock()
        mock_qprocess_class.return_value = mock_process_instance

        window = MainWindow()
        qtbot.addWidget(window)

        # Allow access to the mocked instance and class for assertions
        window.mock_pandoc_process_instance = mock_process_instance
        window.MockQProcessClass = mock_qprocess_class
        yield window # provide the patched window to the test
        window.close()


@pytest.mark.smoke
def test_pandoc_call_structure(main_window_mocked_pandoc):
    """Test that run_pandoc_conversion attempts to call QProcess with pandoc."""
    window = main_window_mocked_pandoc
    mock_process_instance = window.mock_pandoc_process_instance

    window.editor.setPlainText("# Test")
    # Directly call run_pandoc_conversion, bypassing the timer for this direct test
    window.run_pandoc_conversion()

    # Check if QProcess.start was called with "pandoc" and some arguments
    mock_process_instance.start.assert_called_once()
    args_called = mock_process_instance.start.call_args[0]
    assert args_called[0] == window.pandoc_path # Check command
    assert isinstance(args_called[1], list)    # Check args is a list

    # Check that write was called (to send markdown to pandoc stdin)
    mock_process_instance.write.assert_called_once()
    # Check that closeWriteChannel was called
    mock_process_instance.closeWriteChannel.assert_called_once()


@pytest.mark.smoke
def test_pandoc_conversion_success_updates_preview(main_window_mocked_pandoc):
    """Test that successful Pandoc conversion updates the preview widget."""
    window = main_window_mocked_pandoc
    mock_process = window.mock_pandoc_process_instance

    test_markdown = "**Hello**"
    expected_html = "<p><strong>Hello</strong></p>" # Simplified, Pandoc might add more

    # Configure the mock process for a successful run
    mock_process.exitStatus.return_value = QProcess.NormalExit
    mock_process.exitCode.return_value = 0
    # Pandoc output is on stdout
    mock_process.readAllStandardOutput.return_value = expected_html.encode('utf-8')
    mock_process.readAllStandardError.return_value = b"" # No error output

    window.editor.setPlainText(test_markdown)
    window.run_pandoc_conversion() # Call directly

    # The finished signal should be connected and trigger _on_pandoc_finished
    # We can simulate the 'finished' signal if direct call doesn't trigger it via mock
    # For QProcess, finished signal is (int, QProcess.ExitStatus)
    # Here, we directly call _on_pandoc_finished for simplicity as QProcess is mocked.
    # In a real QProcess test, you'd connect a QSignalSpy to the finished signal.
    window._on_pandoc_finished()

    assert expected_html in window.preview_widget.toHtml()


@pytest.mark.smoke
def test_pandoc_conversion_failure_updates_preview(main_window_mocked_pandoc):
    """Test that failed Pandoc conversion shows an error in the preview."""
    window = main_window_mocked_pandoc
    mock_process = window.mock_pandoc_process_instance

    error_message = "Pandoc failed miserably."
    # Configure the mock process for a failed run
    mock_process.exitStatus.return_value = QProcess.NormalExit # Or Crashed
    mock_process.exitCode.return_value = 1 # Non-zero exit code
    mock_process.readAllStandardError.return_value = error_message.encode('utf-8')
    mock_process.readAllStandardOutput.return_value = b""

    window.editor.setPlainText("some markdown that will fail")
    window.run_pandoc_conversion()
    window._on_pandoc_finished() # Simulate completion

    assert error_message in window.preview_widget.toPlainText() # Placeholder text shows errors


def test_pandoc_path_configurable(qtbot, qt_app):
    """Test if pandoc path can be changed (conceptual)."""
    # This test is more about ensuring the structure allows for it.
    # Actual config loading is not yet implemented.
    window = MainWindow()
    qtbot.addWidget(window)
    initial_path = window.pandoc_path
    window.pandoc_path = "/usr/bin/custom_pandoc"
    assert window.pandoc_path == "/usr/bin/custom_pandoc"
    window.pandoc_path = initial_path # Reset for other tests
    window.close()

# TODO: Add tests for:
# - Debounce timer for Pandoc updates (using qtbot.waitSignal)
# - Handling of Pandoc not being found (QProcess.errorOccurred)
# - Specific Pandoc extensions being passed correctly in args
# - Large input handling (if performance becomes an issue)
