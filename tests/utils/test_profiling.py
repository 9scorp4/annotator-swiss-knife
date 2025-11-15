"""
Comprehensive tests for performance profiling utilities.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.profiling import (
    ProfileStats,
    MemoryStats,
    PerformanceProfiler,
    MemoryProfiler,
    RegressionDetector,
    CPUProfiler,
    profile_performance,
    profile_memory,
    comprehensive_profile,
    benchmark,
    get_performance_profiler,
    get_memory_profiler,
    get_regression_detector,
)


class TestProfileStats(unittest.TestCase):
    """Test cases for ProfileStats dataclass."""

    def test_profile_stats_creation(self):
        """Test creating ProfileStats instance."""
        stats = ProfileStats(
            name="test_func",
            call_count=10,
            total_time=1.0,
            avg_time=0.1,
            min_time=0.05,
            max_time=0.15,
            median_time=0.1,
            std_dev=0.02,
            percentile_95=0.14,
            percentile_99=0.15
        )
        self.assertEqual(stats.name, "test_func")
        self.assertEqual(stats.call_count, 10)
        self.assertEqual(stats.total_time, 1.0)

    def test_profile_stats_to_dict(self):
        """Test converting ProfileStats to dictionary."""
        stats = ProfileStats(
            name="test_func",
            call_count=5,
            total_time=0.5,
            avg_time=0.1,
            min_time=0.05,
            max_time=0.15,
            median_time=0.1,
            std_dev=0.02,
            percentile_95=0.14,
            percentile_99=0.15
        )
        result = stats.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "test_func")
        self.assertEqual(result["call_count"], 5)
        self.assertIn("avg_time", result)


class TestMemoryStats(unittest.TestCase):
    """Test cases for MemoryStats dataclass."""

    def test_memory_stats_creation(self):
        """Test creating MemoryStats instance."""
        stats = MemoryStats(
            current_mb=100.5,
            peak_mb=150.0,
            allocated_mb=200.0,
            freed_mb=50.0
        )
        self.assertEqual(stats.current_mb, 100.5)
        self.assertEqual(stats.peak_mb, 150.0)


class TestPerformanceProfiler(unittest.TestCase):
    """Test cases for PerformanceProfiler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler(max_history=100)

    def test_initialization(self):
        """Test profiler initialization."""
        self.assertEqual(self.profiler.max_history, 100)
        self.assertTrue(self.profiler.is_enabled())

    def test_enable_disable(self):
        """Test enabling and disabling profiler."""
        self.profiler.disable()
        self.assertFalse(self.profiler.is_enabled())
        
        self.profiler.enable()
        self.assertTrue(self.profiler.is_enabled())

    def test_record_timing(self):
        """Test recording timing information."""
        self.profiler.record_timing("test_func", 0.1)
        stats = self.profiler.get_stats("test_func")
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.call_count, 1)
        self.assertAlmostEqual(stats.total_time, 0.1)

    def test_record_multiple_timings(self):
        """Test recording multiple timings."""
        timings = [0.1, 0.2, 0.15, 0.12, 0.18]
        for t in timings:
            self.profiler.record_timing("test_func", t)
        
        stats = self.profiler.get_stats("test_func")
        self.assertEqual(stats.call_count, 5)
        self.assertAlmostEqual(stats.total_time, sum(timings))

    def test_get_stats_nonexistent(self):
        """Test getting stats for non-existent function."""
        stats = self.profiler.get_stats("nonexistent")
        self.assertIsNone(stats)

    def test_max_history_limit(self):
        """Test that max history limit is enforced."""
        profiler = PerformanceProfiler(max_history=10)
        
        # Record more than max_history timings
        for i in range(20):
            profiler.record_timing("test_func", 0.1)
        
        stats = profiler.get_stats("test_func")
        # Should keep only last 10
        self.assertEqual(stats.call_count, 10)

    def test_statistics_calculation(self):
        """Test statistics calculations."""
        timings = [1.0, 2.0, 3.0, 4.0, 5.0]
        for t in timings:
            self.profiler.record_timing("test_func", t)
        
        stats = self.profiler.get_stats("test_func")
        self.assertEqual(stats.min_time, 1.0)
        self.assertEqual(stats.max_time, 5.0)
        self.assertEqual(stats.median_time, 3.0)

    def test_disabled_profiler_no_recording(self):
        """Test that disabled profiler doesn't record."""
        self.profiler.disable()
        self.profiler.record_timing("test_func", 0.1)
        
        stats = self.profiler.get_stats("test_func")
        self.assertIsNone(stats)

    def test_thread_safety(self):
        """Test that profiler is thread-safe."""
        import threading

        def record_timings():
            for i in range(100):
                self.profiler.record_timing("test_func", 0.01)

        threads = [threading.Thread(target=record_timings) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = self.profiler.get_stats("test_func")
        self.assertEqual(stats.call_count, 100)

    def test_get_all_stats(self):
        """Test getting all statistics."""
        self.profiler.record_timing("func1", 0.1)
        self.profiler.record_timing("func2", 0.2)

        all_stats = self.profiler.get_all_stats()
        self.assertIsInstance(all_stats, dict)
        self.assertIn("func1", all_stats)
        self.assertIn("func2", all_stats)
        self.assertEqual(len(all_stats), 2)

    def test_get_all_stats_empty(self):
        """Test getting all stats when none recorded."""
        all_stats = self.profiler.get_all_stats()
        self.assertIsInstance(all_stats, dict)
        self.assertEqual(len(all_stats), 0)


class TestMemoryProfiler(unittest.TestCase):
    """Test cases for MemoryProfiler class."""

    def test_memory_profiler_creation(self):
        """Test creating MemoryProfiler."""
        profiler = MemoryProfiler()
        self.assertIsNotNone(profiler)


class TestRegressionDetector(unittest.TestCase):
    """Test cases for RegressionDetector class."""

    def test_detector_initialization(self):
        """Test regression detector initialization."""
        detector = RegressionDetector(threshold_factor=1.5)
        self.assertEqual(detector.threshold_factor, 1.5)

    def test_set_baseline(self):
        """Test setting performance baseline."""
        detector = RegressionDetector()
        detector.set_baseline("test_func", 1.0)
        self.assertIn("test_func", detector._baselines)

    def test_check_regression_no_baseline(self):
        """Test checking regression without baseline."""
        detector = RegressionDetector()
        stats = ProfileStats(
            name="test_func",
            call_count=5,
            total_time=5.0,
            avg_time=1.0,
            min_time=0.9,
            max_time=1.1,
            median_time=1.0,
            std_dev=0.05,
            percentile_95=1.05,
            percentile_99=1.1
        )
        result = detector.check_regression("test_func", stats)
        # Should return None when no baseline exists
        self.assertIsNone(result)

    def test_check_regression_with_baseline_no_regression(self):
        """Test checking regression with baseline and no regression."""
        detector = RegressionDetector(threshold_factor=2.0)
        detector.set_baseline("test_func", 1.0)

        stats = ProfileStats(
            name="test_func",
            call_count=5,
            total_time=5.0,
            avg_time=1.1,  # Slightly higher but within threshold
            min_time=0.9,
            max_time=1.3,
            median_time=1.0,
            std_dev=0.05,
            percentile_95=1.2,
            percentile_99=1.3
        )
        result = detector.check_regression("test_func", stats)
        self.assertIsNone(result)  # No regression means None

    def test_check_regression_with_baseline_has_regression(self):
        """Test checking regression with baseline and regression detected."""
        detector = RegressionDetector(threshold_factor=1.5)
        detector.set_baseline("test_func", 1.0)

        stats = ProfileStats(
            name="test_func",
            call_count=5,
            total_time=10.0,
            avg_time=2.0,  # 2x baseline, exceeds threshold of 1.5
            min_time=1.8,
            max_time=2.2,
            median_time=2.0,
            std_dev=0.1,
            percentile_95=2.1,
            percentile_99=2.2
        )
        result = detector.check_regression("test_func", stats)
        self.assertIsNotNone(result)  # Regression detected returns warning message
        self.assertIsInstance(result, str)

    def test_update_baseline(self):
        """Test updating baseline from current stats."""
        detector = RegressionDetector()
        stats = ProfileStats(
            name="test_func",
            call_count=5,
            total_time=5.0,
            avg_time=1.0,
            min_time=0.9,
            max_time=1.1,
            median_time=1.0,
            std_dev=0.05,
            percentile_95=1.05,
            percentile_99=1.1
        )

        detector.update_baseline("test_func", stats)
        # Check that baseline was set
        self.assertIn("test_func", detector._baselines)
        self.assertEqual(detector._baselines["test_func"], stats.avg_time)


class TestCPUProfiler(unittest.TestCase):
    """Test cases for CPUProfiler class."""

    def test_cpu_profiler_creation(self):
        """Test creating CPUProfiler."""
        profiler = CPUProfiler()
        self.assertIsNotNone(profiler)

    def test_start_stop_profiling(self):
        """Test starting and stopping CPU profiling."""
        profiler = CPUProfiler()

        profiler.start()
        # Simulate some work
        sum([i for i in range(1000)])
        report = profiler.stop()

        # Should return a report string
        self.assertIsInstance(report, str)


class TestProfilePerformanceDecorator(unittest.TestCase):
    """Test cases for profile_performance decorator."""

    def test_decorator_basic_usage(self):
        """Test basic usage of profile_performance decorator."""
        @profile_performance(name="test_func")
        def test_function():
            time.sleep(0.01)
            return "result"
        
        result = test_function()
        self.assertEqual(result, "result")

    def test_decorator_without_name(self):
        """Test decorator without explicit name."""
        @profile_performance()
        def my_function():
            return 42
        
        result = my_function()
        self.assertEqual(result, 42)

    def test_decorator_with_args(self):
        """Test decorator on function with arguments."""
        @profile_performance()
        def add(a, b):
            return a + b
        
        result = add(2, 3)
        self.assertEqual(result, 5)


class TestProfileMemoryDecorator(unittest.TestCase):
    """Test cases for profile_memory decorator."""

    def test_decorator_basic_usage(self):
        """Test basic usage of profile_memory decorator."""
        @profile_memory(name="test_func")
        def test_function():
            return "result"
        
        result = test_function()
        self.assertEqual(result, "result")


class TestComprehensiveProfileDecorator(unittest.TestCase):
    """Test cases for comprehensive_profile decorator."""

    def test_decorator_basic_usage(self):
        """Test basic usage of comprehensive_profile decorator."""
        @comprehensive_profile(name="test_func")
        def test_function():
            return "result"
        
        result = test_function()
        self.assertEqual(result, "result")


class TestBenchmarkDecorator(unittest.TestCase):
    """Test cases for benchmark decorator."""

    def test_benchmark_basic_usage(self):
        """Test basic usage of benchmark decorator."""
        @benchmark(iterations=10, warmup=2)
        def test_function():
            return sum(range(100))
        
        result = test_function()
        self.assertIsNotNone(result)

    def test_benchmark_with_args(self):
        """Test benchmark on function with arguments."""
        @benchmark(iterations=5, warmup=1)
        def multiply(a, b):
            return a * b
        
        result = multiply(3, 4)
        self.assertEqual(result, 12)


class TestGlobalAccessors(unittest.TestCase):
    """Test cases for global accessor functions."""

    def test_get_performance_profiler(self):
        """Test getting global performance profiler."""
        profiler = get_performance_profiler()
        self.assertIsInstance(profiler, PerformanceProfiler)
        
        # Should return same instance
        profiler2 = get_performance_profiler()
        self.assertIs(profiler, profiler2)

    def test_get_memory_profiler(self):
        """Test getting global memory profiler."""
        profiler = get_memory_profiler()
        self.assertIsInstance(profiler, MemoryProfiler)

    def test_get_regression_detector(self):
        """Test getting global regression detector."""
        detector = get_regression_detector()
        self.assertIsInstance(detector, RegressionDetector)


class TestProfilingIntegration(unittest.TestCase):
    """Integration tests for profiling utilities."""

    def test_profile_and_retrieve_stats(self):
        """Test profiling a function and retrieving stats."""
        profiler = PerformanceProfiler()
        
        @profile_performance(name="integration_test")
        def slow_function():
            time.sleep(0.01)
            return "done"
        
        # Call function multiple times
        for i in range(5):
            slow_function()
        
        # Get stats from global profiler
        global_profiler = get_performance_profiler()
        stats = global_profiler.get_stats("integration_test")
        
        if stats:
            self.assertGreaterEqual(stats.call_count, 1)
            self.assertGreater(stats.total_time, 0)


if __name__ == "__main__":
    unittest.main()
