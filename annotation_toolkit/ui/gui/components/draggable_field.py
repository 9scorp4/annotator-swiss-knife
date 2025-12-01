"""
Draggable Field Frame Component.

Provides a draggable field frame with drag-and-drop reordering capabilities.
"""

from typing import Optional, Callable

from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QFont, QDrag
from PyQt5.QtWidgets import QFrame, QLabel

from ..utils.fonts import FontManager


class DraggableFieldFrame(QFrame):
    """
    Draggable field frame for text collector with drag-and-drop reordering.

    This component provides visual feedback and handles drag-and-drop events
    for reordering fields within a container.
    """

    def __init__(self, parent=None, reorder_callback: Optional[Callable[[int, int], None]] = None):
        """
        Initialize draggable field frame.

        Args:
            parent: Parent widget
            reorder_callback: Callback function to call when reordering occurs.
                            Should accept (source_index, target_index) parameters.
        """
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.reorder_callback = reorder_callback

        # Add drag handle indicator (visual cue)
        self.drag_indicator = QLabel("⋮⋮")
        self.drag_indicator.setFont(FontManager.get_font(size=FontManager.SIZE_LG, bold=True))
        self.drag_indicator.setFixedSize(20, 38)
        self.drag_indicator.setAlignment(Qt.AlignCenter)
        self.drag_indicator.setCursor(Qt.OpenHandCursor)
        self.drag_indicator.setToolTip("Drag to reorder")

    def mousePressEvent(self, event):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.LeftButton:
            # Only start drag from drag indicator area (left 50 pixels)
            if event.pos().x() < 50:
                self.drag_start_position = event.pos()
                self.drag_indicator.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_position is None:
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return

        # Start drag operation
        drag = QDrag(self)
        mime_data = QMimeData()

        # Store the widget index
        parent_widget = self.parent()
        if parent_widget:
            layout = parent_widget.layout()
            if layout:
                index = layout.indexOf(self)
                mime_data.setText(str(index))

        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)
        self.drag_indicator.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.drag_start_position = None
        self.drag_indicator.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event to reorder fields."""
        if not event.mimeData().hasText():
            return

        # Get the source index
        source_index = int(event.mimeData().text())

        # Get the target index (this widget's position)
        parent_widget = self.parent()
        if not parent_widget:
            return

        layout = parent_widget.layout()
        if not layout:
            return

        target_index = layout.indexOf(self)

        # Notify via callback
        if self.reorder_callback:
            self.reorder_callback(source_index, target_index)

        event.acceptProposedAction()
