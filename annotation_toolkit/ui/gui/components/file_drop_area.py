"""
FileDropArea component - Drag and drop file input area.

Provides a modern file input with drag & drop support and visual feedback.
"""

from typing import Callable, List, Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPalette
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog


class FileDropArea(QFrame):
    """
    Drag-and-drop file input area with visual feedback.

    Signals:
        files_dropped: Emitted when files are dropped (list of file paths)
    """

    files_dropped = pyqtSignal(list)

    def __init__(
        self,
        text: str = "Drag & drop files here or click to browse",
        file_filter: str = "All Files (*.*)",
        multiple: bool = False,
        parent=None
    ):
        """
        Initialize the file drop area.

        Args:
            text: Placeholder text
            file_filter: QFileDialog file filter
            multiple: Allow multiple file selection
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_filter = file_filter
        self.multiple = multiple
        self.selected_files: List[str] = []

        self.setAcceptDrops(True)
        self._init_ui(text)
        self._apply_default_style()

    def _init_ui(self, text: str):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Drop icon/label
        self.drop_label = QLabel("📁")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.drop_label)

        # Text label
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(self.text_label)

        # Browse button
        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.browse_btn.clicked.connect(self._browse_files)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)

        # Selected files label
        self.files_label = QLabel("")
        self.files_label.setAlignment(Qt.AlignCenter)
        self.files_label.setWordWrap(True)
        self.files_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #27ae60;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.files_label)

    def _apply_default_style(self):
        """Apply default styling."""
        self.setObjectName("fileDropArea")
        self.setStyleSheet("""
            #fileDropArea {
                background-color: rgba(52, 152, 219, 0.05);
                border: 2px dashed #bdc3c7;
                border-radius: 12px;
                min-height: 200px;
            }
            #fileDropArea:hover {
                background-color: rgba(52, 152, 219, 0.1);
                border-color: #3498db;
            }
        """)

    def _apply_drag_style(self):
        """Apply styling during drag over."""
        self.setStyleSheet("""
            #fileDropArea {
                background-color: rgba(52, 152, 219, 0.2);
                border: 2px solid #3498db;
                border-radius: 12px;
                min-height: 200px;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._apply_drag_style()
            self.drop_label.setText("📥")

    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self._apply_default_style()
        self.drop_label.setText("📁")

    def dropEvent(self, event: QDropEvent):
        """Handle file drop event."""
        self._apply_default_style()
        self.drop_label.setText("📁")

        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)

        if files:
            self.selected_files = files if self.multiple else [files[0]]
            self._update_files_label()
            self.files_dropped.emit(self.selected_files)

    def _browse_files(self):
        """Open file browser dialog."""
        if self.multiple:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files",
                "",
                self.file_filter
            )
            if files:
                self.selected_files = files
                self._update_files_label()
                self.files_dropped.emit(self.selected_files)
        else:
            file, _ = QFileDialog.getOpenFileName(
                self,
                "Select File",
                "",
                self.file_filter
            )
            if file:
                self.selected_files = [file]
                self._update_files_label()
                self.files_dropped.emit(self.selected_files)

    def _update_files_label(self):
        """Update the label showing selected files."""
        if not self.selected_files:
            self.files_label.setText("")
            return

        if len(self.selected_files) == 1:
            file_name = self.selected_files[0].split("/")[-1]
            self.files_label.setText(f"✓ Selected: {file_name}")
        else:
            self.files_label.setText(f"✓ Selected {len(self.selected_files)} files")

    def clear(self):
        """Clear selected files."""
        self.selected_files = []
        self.files_label.setText("")

    def get_files(self) -> List[str]:
        """
        Get the list of selected files.

        Returns:
            List of file paths
        """
        return self.selected_files
