"""
Performance profiling utilities.

This module provides tools for profiling performance, collecting metrics,
and detecting performance regressions.
"""

import time
import functools
import threading
import statistics
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import cProfile
import pstats
import io
from pathlib import Path

from .logger import get_logger
from .structured_logging import get_structured_logger, PerformanceMetrics

logger = get_logger()


@dataclass
class ProfileStats:
    """Performance statistics for a function or operation."""
    name: str
    call_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    percentile_95: float
    percentile_99: float
    recent_times: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'call_count': self.call_count,
            'total_time': self.total_time,
            'avg_time': self.avg_time,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'median_time': self.median_time,
            'std_dev': self.std_dev,
            'percentile_95': self.percentile_95,
            'percentile_99': self.percentile_99
        }


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    current_mb: float
    peak_mb: float
    allocated_mb: float
    freed_mb: float


class PerformanceProfiler:
    """Thread-safe performance profiler."""

    def __init__(self, max_history: int = 1000):
        """
        Initialize performance profiler.

        Args:
            max_history: Maximum number of timing records to keep per function.
        """
        self.max_history = max_history
        # Use deque with maxlen for O(1) append with automatic eviction
        self._stats: Dict[str, deque] = {}
        self._lock = threading.Lock()
        self._enabled = True

    def enable(self):
        """Enable profiling."""
        self._enabled = True

    def disable(self):
        """Disable profiling."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if profiling is enabled."""
        return self._enabled

    def record_timing(self, name: str, duration: float):
        """
        Record timing for a function or operation.

        Args:
            name: Name of the function/operation.
            duration: Duration in seconds.
        """
        if not self._enabled:
            return

        with self._lock:
            # Create deque with maxlen on first access (automatic eviction)
            if name not in self._stats:
                self._stats[name] = deque(maxlen=self.max_history)
            self._stats[name].append(duration)

    def get_stats(self, name: str) -> Optional[ProfileStats]:
        """
        Get statistics for a function or operation.

        Args:
            name: Name of the function/operation.

        Returns:
            Profile statistics or None if no data.
        """
        with self._lock:
            if name not in self._stats or not self._stats[name]:
                return None

            timings = self._stats[name].copy()

        if not timings:
            return None

        # Calculate statistics
        total_time = sum(timings)
        call_count = len(timings)
        avg_time = total_time / call_count
        min_time = min(timings)
        max_time = max(timings)

        sorted_timings = sorted(timings)
        median_time = statistics.median(sorted_timings)

        # Standard deviation
        std_dev = statistics.stdev(timings) if len(timings) > 1 else 0.0

        # Percentiles
        percentile_95 = self._percentile(sorted_timings, 95)
        percentile_99 = self._percentile(sorted_timings, 99)

        return ProfileStats(
            name=name,
            call_count=call_count,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_dev=std_dev,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            recent_times=list(timings)[-10:]  # Last 10 timings (convert deque to list for slicing)
        )

    def get_all_stats(self) -> Dict[str, ProfileStats]:
        """Get statistics for all tracked functions."""
        with self._lock:
            names = list(self._stats.keys())

        result = {}
        for name in names:
            stats = self.get_stats(name)
            if stats:
                result[name] = stats

        return result

    def clear_stats(self, name: Optional[str] = None):
        """
        Clear statistics.

        Args:
            name: Specific function name to clear, or None to clear all.
        """
        with self._lock:
            if name:
                if name in self._stats:
                    del self._stats[name]
            else:
                self._stats.clear()

    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0

        index = (percentile / 100.0) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)

        if lower_index == upper_index:
            return sorted_data[lower_index]

        # Linear interpolation
        weight = index - lower_index
        return (sorted_data[lower_index] * (1 - weight) +
                sorted_data[upper_index] * weight)

    def report(self, top_n: int = 10) -> str:
        """
        Generate a performance report.

        Args:
            top_n: Number of top functions to include by total time.

        Returns:
            Formatted report string.
        """
        all_stats = self.get_all_stats()
        if not all_stats:
            return "No performance data collected."

        # Sort by total time
        sorted_stats = sorted(all_stats.values(),
                            key=lambda x: x.total_time,
                            reverse=True)

        lines = ["Performance Profile Report", "=" * 50]
        lines.append(f"{'Function':<30} {'Calls':<8} {'Total(s)':<10} {'Avg(ms)':<10} {'95th(ms)':<10}")
        lines.append("-" * 70)

        for stats in sorted_stats[:top_n]:
            lines.append(
                f"{stats.name:<30} "
                f"{stats.call_count:<8} "
                f"{stats.total_time:<10.3f} "
                f"{stats.avg_time * 1000:<10.2f} "
                f"{stats.percentile_95 * 1000:<10.2f}"
            )

        return "\n".join(lines)


class MemoryProfiler:
    """Memory usage profiler."""

    def __init__(self):
        """Initialize memory profiler."""
        self._enabled = True
        self._peak_memory = 0.0
        self._current_memory = 0.0

    def enable(self):
        """Enable memory profiling."""
        self._enabled = True

    def disable(self):
        """Disable memory profiling."""
        self._enabled = False

    def get_current_memory(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Memory usage in MB, or 0 if psutil not available.
        """
        if not self._enabled:
            return 0.0

        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self._current_memory = memory_mb
            self._peak_memory = max(self._peak_memory, memory_mb)
            return memory_mb
        except ImportError:
            logger.warning("psutil not available for memory profiling")
            return 0.0

    def get_memory_stats(self) -> MemoryStats:
        """Get memory statistics."""
        current = self.get_current_memory()
        return MemoryStats(
            current_mb=current,
            peak_mb=self._peak_memory,
            allocated_mb=0.0,  # Would need more detailed tracking
            freed_mb=0.0
        )

    def reset_peak(self):
        """Reset peak memory tracking."""
        self._peak_memory = self.get_current_memory()


class RegressionDetector:
    """Detects performance regressions."""

    def __init__(self, threshold_factor: float = 1.5,
                 min_samples: int = 10):
        """
        Initialize regression detector.

        Args:
            threshold_factor: Factor by which performance must degrade to trigger alert.
            min_samples: Minimum number of samples needed for comparison.
        """
        self.threshold_factor = threshold_factor
        self.min_samples = min_samples
        self._baselines: Dict[str, float] = {}

    def set_baseline(self, name: str, baseline_time: float):
        """Set performance baseline for a function."""
        self._baselines[name] = baseline_time

    def check_regression(self, name: str, current_stats: ProfileStats) -> Optional[str]:
        """
        Check if current performance shows regression.

        Args:
            name: Function name.
            current_stats: Current performance statistics.

        Returns:
            Warning message if regression detected, None otherwise.
        """
        if name not in self._baselines:
            # Auto-set baseline if we have enough samples
            if current_stats.call_count >= self.min_samples:
                self._baselines[name] = current_stats.avg_time
            return None

        baseline = self._baselines[name]
        current_avg = current_stats.avg_time

        if current_avg > baseline * self.threshold_factor:
            degradation = (current_avg / baseline - 1) * 100
            return (f"Performance regression detected in {name}: "
                   f"{degradation:.1f}% slower than baseline "
                   f"(current: {current_avg*1000:.2f}ms, "
                   f"baseline: {baseline*1000:.2f}ms)")

        return None

    def update_baseline(self, name: str, current_stats: ProfileStats):
        """Update baseline with current performance if it's better."""
        if name in self._baselines:
            if current_stats.avg_time < self._baselines[name]:
                self._baselines[name] = current_stats.avg_time
        else:
            self._baselines[name] = current_stats.avg_time


class CPUProfiler:
    """CPU profiler using cProfile."""

    def __init__(self):
        """Initialize CPU profiler."""
        self._profiler = None
        self._enabled = False

    def start(self):
        """Start CPU profiling."""
        if self._profiler is not None:
            self.stop()

        self._profiler = cProfile.Profile()
        self._profiler.enable()
        self._enabled = True
        logger.info("CPU profiling started")

    def stop(self) -> Optional[str]:
        """
        Stop CPU profiling and return report.

        Returns:
            Formatted profiling report or None if not running.
        """
        if self._profiler is None or not self._enabled:
            return None

        self._profiler.disable()
        self._enabled = False

        # Generate report
        s = io.StringIO()
        stats = pstats.Stats(self._profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions

        logger.info("CPU profiling stopped")
        return s.getvalue()

    def save_profile(self, filename: Union[str, Path]):
        """Save profile data to file."""
        if self._profiler is None:
            return

        self._profiler.dump_stats(str(filename))

    def is_running(self) -> bool:
        """Check if profiler is running."""
        return self._enabled


# Global profiler instances
_performance_profiler: Optional[PerformanceProfiler] = None
_memory_profiler: Optional[MemoryProfiler] = None
_regression_detector: Optional[RegressionDetector] = None


def get_performance_profiler() -> PerformanceProfiler:
    """Get global performance profiler."""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler


def get_memory_profiler() -> MemoryProfiler:
    """Get global memory profiler."""
    global _memory_profiler
    if _memory_profiler is None:
        _memory_profiler = MemoryProfiler()
    return _memory_profiler


def get_regression_detector() -> RegressionDetector:
    """Get global regression detector."""
    global _regression_detector
    if _regression_detector is None:
        _regression_detector = RegressionDetector()
    return _regression_detector


# Decorators
def profile_performance(name: Optional[str] = None,
                       check_regression: bool = False):
    """
    Decorator for profiling function performance.

    Args:
        name: Custom name for the function (defaults to function name).
        check_regression: Whether to check for performance regressions.

    Example:
        @profile_performance(check_regression=True)
        def expensive_operation():
            # some expensive operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        func_name = name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = get_performance_profiler()
            if not profiler.is_enabled():
                return func(*args, **kwargs)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                profiler.record_timing(func_name, duration)

                # Check for regression if requested
                if check_regression:
                    detector = get_regression_detector()
                    stats = profiler.get_stats(func_name)
                    if stats and stats.call_count >= 5:  # Need some samples
                        warning = detector.check_regression(func_name, stats)
                        if warning:
                            logger.warning(warning)

        return wrapper
    return decorator


def profile_memory(name: Optional[str] = None):
    """
    Decorator for profiling memory usage.

    Args:
        name: Custom name for the function.

    Example:
        @profile_memory()
        def memory_intensive_operation():
            # operation that uses lots of memory
            pass
    """
    def decorator(func: Callable) -> Callable:
        func_name = name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            memory_profiler = get_memory_profiler()
            if not memory_profiler._enabled:
                return func(*args, **kwargs)

            # Record memory before
            memory_before = memory_profiler.get_current_memory()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Record memory after
                memory_after = memory_profiler.get_current_memory()
                memory_delta = memory_after - memory_before

                if abs(memory_delta) > 1.0:  # Only log if significant change
                    structured_logger = get_structured_logger()
                    structured_logger.info(
                        f"Memory usage for {func_name}",
                        component="memory_profiler",
                        extra_data={
                            "function": func_name,
                            "memory_before_mb": memory_before,
                            "memory_after_mb": memory_after,
                            "memory_delta_mb": memory_delta
                        }
                    )

        return wrapper
    return decorator


def comprehensive_profile(name: Optional[str] = None,
                         check_regression: bool = False,
                         track_memory: bool = True):
    """
    Decorator for comprehensive profiling (performance + memory).

    Args:
        name: Custom name for the function.
        check_regression: Whether to check for performance regressions.
        track_memory: Whether to track memory usage.

    Example:
        @comprehensive_profile(check_regression=True)
        def complex_operation():
            # complex operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Apply multiple decorators
        decorated = func
        if track_memory:
            decorated = profile_memory(name)(decorated)
        decorated = profile_performance(name, check_regression)(decorated)
        return decorated
    return decorator


def benchmark(iterations: int = 1000, warmup: int = 100):
    """
    Decorator for benchmarking functions.

    Args:
        iterations: Number of iterations to run.
        warmup: Number of warmup iterations.

    Example:
        @benchmark(iterations=1000, warmup=50)
        def function_to_benchmark():
            # function to benchmark
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Warmup
            for _ in range(warmup):
                func(*args, **kwargs)

            # Benchmark
            times = []
            for _ in range(iterations):
                start = time.time()
                func(*args, **kwargs)
                times.append(time.time() - start)

            # Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            median_time = statistics.median(times)

            # Log results
            structured_logger = get_structured_logger()
            structured_logger.info(
                f"Benchmark results for {func.__name__}",
                component="benchmark",
                extra_data={
                    "function": func.__name__,
                    "iterations": iterations,
                    "avg_time_ms": avg_time * 1000,
                    "min_time_ms": min_time * 1000,
                    "max_time_ms": max_time * 1000,
                    "median_time_ms": median_time * 1000
                }
            )

            return func(*args, **kwargs)  # Return result of single execution

        return wrapper
    return decorator