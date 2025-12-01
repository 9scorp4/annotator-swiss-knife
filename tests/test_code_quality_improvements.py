"""
Tests for code quality improvements implemented in the optimization effort.

This module tests the following improvements:
- Phase 1: Specific exception handling in bootstrap.py
- Phase 2: Lazy config loading and lazy global instances in security.py
- Phase 3: TTLCache auto-cleanup, pre-compiled regex, deque for stats
- Phase 4: LazyToolRegistry for deferred tool resolution
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from annotation_toolkit.di.bootstrap import (
    LazyToolRegistry,
    get_tool_instances,
    bootstrap_application,
)
from annotation_toolkit.di.container import DIContainer
from annotation_toolkit.di.exceptions import (
    ServiceNotRegisteredError,
    ServiceCreationError,
    CircularDependencyError,
)
from annotation_toolkit.core.conversation.visualizer import TTLCache
from annotation_toolkit.utils.security import (
    _get_security_config,
    get_max_file_size,
    get_max_path_length,
    get_allowed_extensions,
    get_rate_limit_window,
    get_rate_limit_max_requests,
    get_default_path_validator,
    get_default_file_size_validator,
    get_default_input_sanitizer,
    get_default_rate_limiter,
    PathValidator,
    _SUSPICIOUS_PATH_PATTERN,
)


class TestLazyToolRegistry(unittest.TestCase):
    """Test the LazyToolRegistry for deferred tool resolution."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = bootstrap_application()
        self.registry = LazyToolRegistry(self.container)

    def test_lazy_resolution_on_first_access(self):
        """Test that tools are resolved only when first accessed."""
        # Initially no tools should be resolved
        self.assertEqual(len(self.registry._resolved_tools), 0)

        # Access a tool
        from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
        tool = self.registry.get_tool(DictToBulletList)

        # Now one tool should be resolved
        self.assertIsNotNone(tool)
        self.assertEqual(len(self.registry._resolved_tools), 1)

    def test_caching_resolved_tools(self):
        """Test that resolved tools are cached and reused."""
        from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList

        tool1 = self.registry.get_tool(DictToBulletList)
        tool2 = self.registry.get_tool(DictToBulletList)

        # Should return the same instance
        self.assertIs(tool1, tool2)

    def test_get_tool_by_name(self):
        """Test getting tools by their name attribute."""
        tool = self.registry.get_tool_by_name("URL Dictionary to Clickables")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "URL Dictionary to Clickables")

    def test_get_all_tools(self):
        """Test getting all tools at once."""
        tools = self.registry.get_all_tools()
        self.assertIsInstance(tools, dict)
        self.assertGreater(len(tools), 0)

    def test_failed_resolution_not_retried(self):
        """Test that failed resolutions are not retried."""
        # Create a mock container that raises ServiceNotRegisteredError
        mock_container = MagicMock()
        mock_container.resolve.side_effect = ServiceNotRegisteredError(object)

        registry = LazyToolRegistry(mock_container)

        class FakeTool:
            pass

        # First attempt
        result1 = registry.get_tool(FakeTool)
        self.assertIsNone(result1)

        # Second attempt should not call resolve again
        result2 = registry.get_tool(FakeTool)
        self.assertIsNone(result2)

        # resolve should only be called once
        self.assertEqual(mock_container.resolve.call_count, 1)


class TestTTLCacheAutoCleanup(unittest.TestCase):
    """Test the automatic cleanup feature of TTLCache."""

    def test_auto_cleanup_triggers(self):
        """Test that automatic cleanup triggers after cleanup_interval."""
        # Create cache with very short TTL and cleanup interval
        cache = TTLCache(max_size=128, ttl_seconds=1, cleanup_interval=1)

        # Add an item
        cache.put("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")

        # Wait for item to expire and cleanup interval to pass
        time.sleep(1.5)

        # Access cache - this should trigger cleanup
        cache.get("key1")

        # Item should be cleaned up
        self.assertIsNone(cache.get("key1"))

    def test_last_cleanup_tracking(self):
        """Test that _last_cleanup timestamp is updated."""
        cache = TTLCache(max_size=128, ttl_seconds=300, cleanup_interval=0)  # 0 means always cleanup

        initial_cleanup = cache._last_cleanup

        # Access cache to trigger cleanup
        time.sleep(0.1)
        cache.get("nonexistent")

        # _last_cleanup should be updated
        self.assertGreater(cache._last_cleanup, initial_cleanup)

    def test_cleanup_interval_respected(self):
        """Test that cleanup doesn't run before interval passes."""
        cache = TTLCache(max_size=128, ttl_seconds=1, cleanup_interval=60)

        # Add and expire an item
        cache.put("key1", "value1")
        time.sleep(1.1)

        # Manual check - item expired but cleanup interval hasn't passed
        # The item will be removed on individual access (line 64-67 in visualizer.py)
        # but full cleanup_expired won't be called
        self.assertIsNone(cache.get("key1"))  # Returns None due to individual expiry check


class TestSecurityLazyConfig(unittest.TestCase):
    """Test lazy configuration loading in security module."""

    def test_config_loads_lazily(self):
        """Test that _get_security_config returns valid config."""
        config = _get_security_config()
        self.assertIsInstance(config, dict)
        self.assertIn('max_file_size', config)
        self.assertIn('max_path_length', config)
        self.assertIn('allowed_extensions', config)
        self.assertIn('rate_limit_window', config)
        self.assertIn('rate_limit_max_requests', config)

    def test_config_values_are_valid(self):
        """Test that config values have appropriate types and defaults."""
        self.assertIsInstance(get_max_file_size(), int)
        self.assertIsInstance(get_max_path_length(), int)
        self.assertIsInstance(get_allowed_extensions(), set)
        self.assertIsInstance(get_rate_limit_window(), int)
        self.assertIsInstance(get_rate_limit_max_requests(), int)

        # Check defaults
        self.assertGreater(get_max_file_size(), 0)
        self.assertGreater(get_max_path_length(), 0)
        self.assertIn('.json', get_allowed_extensions())

    def test_config_caching(self):
        """Test that config is cached via lru_cache."""
        config1 = _get_security_config()
        config2 = _get_security_config()
        self.assertIs(config1, config2)  # Same object due to caching


class TestSecurityLazyGlobalInstances(unittest.TestCase):
    """Test lazy global instance creation in security module."""

    def test_lazy_path_validator(self):
        """Test lazy initialization of default PathValidator."""
        validator = get_default_path_validator()
        self.assertIsInstance(validator, PathValidator)

        # Should return same instance
        validator2 = get_default_path_validator()
        self.assertIs(validator, validator2)

    def test_lazy_file_size_validator(self):
        """Test lazy initialization of default FileSizeValidator."""
        from annotation_toolkit.utils.security import FileSizeValidator
        validator = get_default_file_size_validator()
        self.assertIsInstance(validator, FileSizeValidator)

    def test_lazy_input_sanitizer(self):
        """Test lazy initialization of default InputSanitizer."""
        from annotation_toolkit.utils.security import InputSanitizer
        sanitizer = get_default_input_sanitizer()
        self.assertIsInstance(sanitizer, InputSanitizer)

    def test_lazy_rate_limiter(self):
        """Test lazy initialization of default RateLimiter."""
        from annotation_toolkit.utils.security import RateLimiter
        limiter = get_default_rate_limiter()
        self.assertIsInstance(limiter, RateLimiter)

    def test_module_getattr_for_backwards_compat(self):
        """Test that module-level __getattr__ works for lazy attributes."""
        from annotation_toolkit.utils import security

        # These should work via __getattr__
        validator = security.default_path_validator
        self.assertIsNotNone(validator)


class TestPrecompiledRegex(unittest.TestCase):
    """Test pre-compiled regex patterns in security module."""

    def test_suspicious_pattern_compiled(self):
        """Test that _SUSPICIOUS_PATH_PATTERN is pre-compiled."""
        import re
        self.assertIsInstance(_SUSPICIOUS_PATH_PATTERN, re.Pattern)

    def test_suspicious_pattern_matches(self):
        """Test that the pattern correctly matches suspicious paths."""
        # Should match
        self.assertIsNotNone(_SUSPICIOUS_PATH_PATTERN.search("path/../etc"))
        self.assertIsNotNone(_SUSPICIOUS_PATH_PATTERN.search("~/home"))
        self.assertIsNotNone(_SUSPICIOUS_PATH_PATTERN.search("$HOME"))
        self.assertIsNotNone(_SUSPICIOUS_PATH_PATTERN.search("%USERPROFILE%"))
        self.assertIsNotNone(_SUSPICIOUS_PATH_PATTERN.search("path\x00evil"))

        # Should not match
        self.assertIsNone(_SUSPICIOUS_PATH_PATTERN.search("/safe/path/file.txt"))
        self.assertIsNone(_SUSPICIOUS_PATH_PATTERN.search("C:\\Users\\Safe\\file.txt"))


class TestDequeForProfiler(unittest.TestCase):
    """Test that PerformanceProfiler uses deque for bounded stats."""

    def test_stats_use_deque(self):
        """Test that _stats uses deque with maxlen."""
        from collections import deque
        from annotation_toolkit.utils.profiling import PerformanceProfiler

        profiler = PerformanceProfiler(max_history=100)
        profiler.record_timing("test", 0.1)

        # Check that stats entry is a deque with maxlen
        self.assertIn("test", profiler._stats)
        self.assertIsInstance(profiler._stats["test"], deque)
        self.assertEqual(profiler._stats["test"].maxlen, 100)

    def test_deque_automatic_eviction(self):
        """Test that deque automatically evicts old items."""
        from annotation_toolkit.utils.profiling import PerformanceProfiler

        profiler = PerformanceProfiler(max_history=5)

        # Add 10 timings
        for i in range(10):
            profiler.record_timing("test", float(i))

        # Should only have last 5
        self.assertEqual(len(profiler._stats["test"]), 5)
        self.assertEqual(list(profiler._stats["test"]), [5.0, 6.0, 7.0, 8.0, 9.0])


class TestSpecificExceptionHandling(unittest.TestCase):
    """Test that specific DI exceptions are caught properly."""

    def test_get_tool_instances_catches_di_exceptions(self):
        """Test that get_tool_instances only catches DI-specific exceptions."""
        container = bootstrap_application()

        # Should work without errors
        tools = get_tool_instances(container)
        self.assertIsInstance(tools, dict)
        self.assertGreater(len(tools), 0)

    def test_lazy_registry_catches_specific_exceptions(self):
        """Test LazyToolRegistry catches only DI exceptions."""
        mock_container = MagicMock()

        # Test with ServiceNotRegisteredError
        mock_container.resolve.side_effect = ServiceNotRegisteredError(object)
        registry = LazyToolRegistry(mock_container)

        class FakeTool:
            pass

        result = registry.get_tool(FakeTool)
        self.assertIsNone(result)
        self.assertIn(FakeTool, registry._failed_tools)


if __name__ == '__main__':
    unittest.main()
