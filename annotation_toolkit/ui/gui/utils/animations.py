"""
Animation utilities for smooth UI transitions.

This module provides a comprehensive animation system for the Qt application,
including fade, slide, and custom property animations with easing curves.
"""

from typing import Optional, Callable
from PyQt5.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QAbstractAnimation,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    QPoint,
    QRect,
    pyqtSignal,
    QObject,
)
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect


class AnimationManager(QObject):
    """
    Central manager for UI animations.

    Provides high-level animation functions and manages animation lifecycle.
    """

    # Signals
    animation_started = pyqtSignal(str)  # Animation name
    animation_finished = pyqtSignal(str)  # Animation name

    def __init__(self):
        """Initialize the animation manager."""
        super().__init__()
        self._active_animations = {}

    def register_animation(self, name: str, animation: QPropertyAnimation):
        """
        Register an animation for tracking.

        Args:
            name: Unique name for the animation
            animation: The animation object
        """
        self._active_animations[name] = animation
        animation.finished.connect(lambda: self._on_animation_finished(name))

    def _on_animation_finished(self, name: str):
        """Handle animation completion."""
        if name in self._active_animations:
            del self._active_animations[name]
        self.animation_finished.emit(name)

    def stop_all(self):
        """Stop all active animations."""
        for animation in self._active_animations.values():
            animation.stop()
        self._active_animations.clear()


# Global animation manager instance
_animation_manager = AnimationManager()


def get_animation_manager() -> AnimationManager:
    """Get the global animation manager instance."""
    return _animation_manager


# ============================================================================
# FADE ANIMATIONS
# ============================================================================

def fade_in(
    widget: QWidget,
    duration: int = 250,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.OutCubic
) -> QPropertyAnimation:
    """
    Fade in a widget from transparent to opaque.

    Args:
        widget: Widget to animate
        duration: Animation duration in milliseconds
        on_finished: Optional callback when animation completes
        easing: Easing curve type

    Returns:
        QPropertyAnimation: The animation object (already started)
    """
    # Ensure widget has opacity effect
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    # Create animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(easing)

    # Connect callback
    if on_finished:
        animation.finished.connect(on_finished)

    # Make sure widget is visible
    widget.setVisible(True)

    # Start animation
    animation.start(QAbstractAnimation.DeleteWhenStopped)

    return animation


def fade_out(
    widget: QWidget,
    duration: int = 250,
    hide_when_done: bool = True,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.InCubic
) -> QPropertyAnimation:
    """
    Fade out a widget from opaque to transparent.

    Args:
        widget: Widget to animate
        duration: Animation duration in milliseconds
        hide_when_done: Whether to hide widget when animation completes
        on_finished: Optional callback when animation completes
        easing: Easing curve type

    Returns:
        QPropertyAnimation: The animation object (already started)
    """
    # Ensure widget has opacity effect
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    # Create animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(easing)

    # Hide widget when done if requested
    if hide_when_done:
        animation.finished.connect(lambda: widget.setVisible(False))

    # Connect callback
    if on_finished:
        animation.finished.connect(on_finished)

    # Start animation
    animation.start(QAbstractAnimation.DeleteWhenStopped)

    return animation


def fade_transition(
    from_widget: QWidget,
    to_widget: QWidget,
    duration: int = 300,
    on_finished: Optional[Callable] = None
) -> QSequentialAnimationGroup:
    """
    Smoothly transition between two widgets with a crossfade.

    Args:
        from_widget: Widget to fade out
        to_widget: Widget to fade in
        duration: Total transition duration in milliseconds
        on_finished: Optional callback when transition completes

    Returns:
        QSequentialAnimationGroup: The animation group
    """
    # Half duration for each fade
    half_duration = duration // 2

    # Create animation group
    group = QSequentialAnimationGroup()

    # Fade out current widget
    fade_out_anim = fade_out(from_widget, half_duration, hide_when_done=True)

    # Fade in new widget
    fade_in_anim = fade_in(to_widget, half_duration)

    # Note: We can't add the animations to the group because they're already started
    # So we'll just return the group for reference and use callbacks
    if on_finished:
        fade_in_anim.finished.connect(on_finished)

    return group


# ============================================================================
# SLIDE ANIMATIONS
# ============================================================================

def slide_in(
    widget: QWidget,
    direction: str = "left",
    duration: int = 300,
    distance: Optional[int] = None,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.OutCubic
) -> QPropertyAnimation:
    """
    Slide a widget in from a direction.

    Args:
        widget: Widget to animate
        direction: Direction to slide from ("left", "right", "top", "bottom")
        duration: Animation duration in milliseconds
        distance: Slide distance (uses widget width/height if None)
        on_finished: Optional callback when animation completes
        easing: Easing curve type

    Returns:
        QPropertyAnimation: The animation object (already started)
    """
    # Get current position
    current_pos = widget.pos()

    # Calculate distance
    if distance is None:
        if direction in ("left", "right"):
            distance = widget.width()
        else:
            distance = widget.height()

    # Calculate start position
    if direction == "left":
        start_pos = QPoint(current_pos.x() - distance, current_pos.y())
    elif direction == "right":
        start_pos = QPoint(current_pos.x() + distance, current_pos.y())
    elif direction == "top":
        start_pos = QPoint(current_pos.x(), current_pos.y() - distance)
    else:  # bottom
        start_pos = QPoint(current_pos.x(), current_pos.y() + distance)

    # Create animation
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(current_pos)
    animation.setEasingCurve(easing)

    # Connect callback
    if on_finished:
        animation.finished.connect(on_finished)

    # Make sure widget is visible
    widget.setVisible(True)

    # Start animation
    animation.start(QAbstractAnimation.DeleteWhenStopped)

    return animation


def slide_out(
    widget: QWidget,
    direction: str = "left",
    duration: int = 300,
    distance: Optional[int] = None,
    hide_when_done: bool = True,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.InCubic
) -> QPropertyAnimation:
    """
    Slide a widget out to a direction.

    Args:
        widget: Widget to animate
        direction: Direction to slide to ("left", "right", "top", "bottom")
        duration: Animation duration in milliseconds
        distance: Slide distance (uses widget width/height if None)
        hide_when_done: Whether to hide widget when animation completes
        on_finished: Optional callback when animation completes
        easing: Easing curve type

    Returns:
        QPropertyAnimation: The animation object (already started)
    """
    # Get current position
    current_pos = widget.pos()

    # Calculate distance
    if distance is None:
        if direction in ("left", "right"):
            distance = widget.width()
        else:
            distance = widget.height()

    # Calculate end position
    if direction == "left":
        end_pos = QPoint(current_pos.x() - distance, current_pos.y())
    elif direction == "right":
        end_pos = QPoint(current_pos.x() + distance, current_pos.y())
    elif direction == "top":
        end_pos = QPoint(current_pos.x(), current_pos.y() - distance)
    else:  # bottom
        end_pos = QPoint(current_pos.x(), current_pos.y() + distance)

    # Create animation
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(current_pos)
    animation.setEndValue(end_pos)
    animation.setEasingCurve(easing)

    # Hide widget when done if requested
    if hide_when_done:
        animation.finished.connect(lambda: widget.setVisible(False))

    # Connect callback
    if on_finished:
        animation.finished.connect(on_finished)

    # Start animation
    animation.start(QAbstractAnimation.DeleteWhenStopped)

    return animation


# ============================================================================
# PROPERTY ANIMATIONS
# ============================================================================

def animate_opacity(
    widget: QWidget,
    from_opacity: float,
    to_opacity: float,
    duration: int = 250,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.InOutCubic
) -> QPropertyAnimation:
    """
    Animate widget opacity.

    Args:
        widget: Widget to animate
        from_opacity: Starting opacity (0.0 to 1.0)
        to_opacity: Ending opacity (0.0 to 1.0)
        duration: Animation duration in milliseconds
        on_finished: Optional callback when animation completes
        easing: Easing curve type

    Returns:
        QPropertyAnimation: The animation object (already started)
    """
    # Ensure widget has opacity effect
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    # Set initial opacity
    effect.setOpacity(from_opacity)

    # Create animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(from_opacity)
    animation.setEndValue(to_opacity)
    animation.setEasingCurve(easing)

    # Connect callback
    if on_finished:
        animation.finished.connect(on_finished)

    # Start animation
    animation.start(QAbstractAnimation.DeleteWhenStopped)

    return animation


def animate_geometry(
    widget: QWidget,
    from_rect: QRect,
    to_rect: QRect,
    duration: int = 300,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.InOutCubic
) -> QPropertyAnimation:
    """
    Animate widget geometry (position and size).

    Args:
        widget: Widget to animate
        from_rect: Starting geometry
        to_rect: Ending geometry
        duration: Animation duration in milliseconds
        on_finished: Optional callback when animation completes
        easing: Easing curve type

    Returns:
        QPropertyAnimation: The animation object (already started)
    """
    # Create animation
    animation = QPropertyAnimation(widget, b"geometry")
    animation.setDuration(duration)
    animation.setStartValue(from_rect)
    animation.setEndValue(to_rect)
    animation.setEasingCurve(easing)

    # Connect callback
    if on_finished:
        animation.finished.connect(on_finished)

    # Start animation
    animation.start(QAbstractAnimation.DeleteWhenStopped)

    return animation


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_parallel_group(*animations) -> QParallelAnimationGroup:
    """
    Create a parallel animation group from multiple animations.

    Args:
        *animations: Variable number of QPropertyAnimation objects

    Returns:
        QParallelAnimationGroup: Group that runs all animations simultaneously
    """
    group = QParallelAnimationGroup()
    for anim in animations:
        group.addAnimation(anim)
    return group


def create_sequential_group(*animations) -> QSequentialAnimationGroup:
    """
    Create a sequential animation group from multiple animations.

    Args:
        *animations: Variable number of QPropertyAnimation objects

    Returns:
        QSequentialAnimationGroup: Group that runs animations one after another
    """
    group = QSequentialAnimationGroup()
    for anim in animations:
        group.addAnimation(anim)
    return group
