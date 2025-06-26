# widgets.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt

class Card(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("Card") # For styling

        layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle") # For styling
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.content_widget = QWidget() # Placeholder for card content
        layout.addWidget(self.content_widget)

        self.setLayout(layout)
        self.setStyleSheet("""
            #Card {
                background-color: #f0f0f0;
                border-radius: 10px;
                border: 1px solid #cccccc;
                margin: 10px;
                padding: 10px;
            }
            #CardTitle {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)

class FileBrowserCard(Card):
    def __init__(self, parent=None):
        super().__init__("File Browser", parent)
        # Add file browsing widgets to self.content_widget
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.addWidget(QLabel("File list will go here..."))
        # Example: Add a button
        content_layout.addWidget(QPushButton("Open File"))

class SettingsCard(Card):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        # Add settings widgets to self.content_widget
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.addWidget(QLabel("Settings options will go here..."))
        content_layout.addWidget(QPushButton("Change Theme"))

# Add more card types as needed
class RecentFilesCard(Card):
    def __init__(self, parent=None):
        super().__init__("Recent Files", parent)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.addWidget(QLabel("Recent files list..."))

class ProjectExplorerCard(Card):
    def __init__(self, parent=None):
        super().__init__("Project Explorer", parent)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.addWidget(QLabel("Project tree view..."))

class HelpCard(Card):
    def __init__(self, parent=None):
        super().__init__("Help & About", parent)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.addWidget(QLabel("Help information, links to documentation..."))
        content_layout.addWidget(QPushButton("About Pandoc Typora V2"))
