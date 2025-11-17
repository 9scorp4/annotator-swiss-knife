"""
LoadingOverlay component for async operations.

Displays a spinner with glassmorphic blur background.
"""

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import math


class LoadingSpinner(QWidget):
    """Animated loading spinner."""

    def __init__(self, size=40, color=None, parent=None):
        super().__init__(parent)
        self.size = size
        self.color = color or QColor("#4299e1")
        self.angle = 0
        self.setFixedSize(size, size)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(50)  # Update every 50ms

    def _rotate(self):
        """Rotate the spinner."""
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw spinning arcs
        pen = QPen(self.color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # Draw 8 segments with varying opacity
        for i in range(8):
            opacity = 1.0 - (i * 0.12)
            color = QColor(self.color)
            color.setAlphaF(opacity)
            pen.setColor(color)
            painter.setPen(pen)

            angle = self.angle + (i * 45)
            start_angle = angle * 16  # Qt uses 1/16th degree units
            span_angle = 30 * 16

            painter.drawArc(
                5, 5,
                self.size - 10, self.size - 10,
                start_angle, span_angle
            )

    def stop(self):
        """Stop the spinner animation."""
        self.timer.stop()


class LoadingOverlay(QWidget):
    """
    Full-screen loading overlay with spinner and message.
    """

    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.message = message
        self._init_ui()

        # Position over parent
        if parent:
            self.setGeometry(parent.rect())
            parent.installEventFilter(self)

    def _init_ui(self):
        """Initialize the UI."""
        # Semi-transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.5);
            }
        """)

        # Center layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Spinner
        self.spinner = LoadingSpinner(50)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # Message
        message_label = QLabel(self.message)
        message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin-top: 16px;
            }
        """)
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)

    def eventFilter(self, obj, event):
        """Resize with parent."""
        if event.type() == event.Resize and obj == self.parent():
            self.setGeometry(obj.rect())
        return super().eventFilter(obj, event)

    def show_loading(self, parent=None):
        """Show the loading overlay."""
        if parent:
            self.setParent(parent)
            self.setGeometry(parent.rect())
        self.raise_()
        self.show()

    def hide_loading(self):
        """Hide the loading overlay."""
        self.spinner.stop()
        self.hide()
