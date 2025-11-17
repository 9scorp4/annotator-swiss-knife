"""
Error display utilities for widgets.

Provides helpers for displaying inline error banners instead of modal dialogs.
"""

from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ..components import ErrorBanner


class ErrorDisplayMixin:
    """
    Mixin for widgets to easily display inline error banners.

    Usage:
        class MyWidget(QWidget, ErrorDisplayMixin):
            def __init__(self):
                super().__init__()
                self._init_error_container()

            def some_method(self):
                self.show_error("Something went wrong!")
    """

    def _init_error_container(self):
        """
        Initialize the error container.

        Should be called in the widget's __init__ after setting up the main layout.
        Assumes the widget has a main_layout attribute or similar.
        """
        self.error_banners = []

    def show_error(
        self,
        message: str,
        auto_dismiss: int = 5000,
        parent_layout: Optional[QVBoxLayout] = None
    ) -> ErrorBanner:
        """
        Show an inline error banner.

        Args:
            message: Error message to display
            auto_dismiss: Auto-dismiss after N milliseconds (0 = no auto-dismiss)
            parent_layout: Layout to add the banner to. If None, tries to use self.layout()

        Returns:
            The created ErrorBanner instance
        """
        # Clear any existing error banners
        self.clear_errors()

        # Create error banner
        banner = ErrorBanner(message, error_type="error", auto_dismiss=auto_dismiss)
        banner.closed.connect(lambda: self._on_banner_closed(banner))

        # Add to layout
        layout = parent_layout or self.layout()
        if layout:
            layout.insertWidget(0, banner)  # Insert at top
            self.error_banners.append(banner)

        return banner

    def show_warning(
        self,
        message: str,
        auto_dismiss: int = 5000,
        parent_layout: Optional[QVBoxLayout] = None
    ) -> ErrorBanner:
        """Show an inline warning banner."""
        self.clear_errors()

        banner = ErrorBanner(message, error_type="warning", auto_dismiss=auto_dismiss)
        banner.closed.connect(lambda: self._on_banner_closed(banner))

        layout = parent_layout or self.layout()
        if layout:
            layout.insertWidget(0, banner)
            self.error_banners.append(banner)

        return banner

    def show_info(
        self,
        message: str,
        auto_dismiss: int = 3000,
        parent_layout: Optional[QVBoxLayout] = None
    ) -> ErrorBanner:
        """Show an inline info banner."""
        self.clear_errors()

        banner = ErrorBanner(message, error_type="info", auto_dismiss=auto_dismiss)
        banner.closed.connect(lambda: self._on_banner_closed(banner))

        layout = parent_layout or self.layout()
        if layout:
            layout.insertWidget(0, banner)
            self.error_banners.append(banner)

        return banner

    def show_success(
        self,
        message: str,
        auto_dismiss: int = 3000,
        parent_layout: Optional[QVBoxLayout] = None
    ) -> ErrorBanner:
        """Show an inline success banner."""
        self.clear_errors()

        banner = ErrorBanner(message, error_type="success", auto_dismiss=auto_dismiss)
        banner.closed.connect(lambda: self._on_banner_closed(banner))

        layout = parent_layout or self.layout()
        if layout:
            layout.insertWidget(0, banner)
            self.error_banners.append(banner)

        return banner

    def clear_errors(self):
        """Clear all error banners."""
        for banner in self.error_banners[:]:  # Copy list to avoid modification during iteration
            banner.dismiss()
        self.error_banners.clear()

    def _on_banner_closed(self, banner: ErrorBanner):
        """Handle banner close event."""
        if banner in self.error_banners:
            self.error_banners.remove(banner)
