# Performance Guide - Annotation Swiss Knife

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Performance Profiling](#performance-profiling)
3. [Optimization Techniques](#optimization-techniques)
4. [Streaming for Large Files](#streaming-for-large-files)
5. [Caching Strategies](#caching-strategies)
6. [Configuration](#configuration)
7. [Performance Benchmarks](#performance-benchmarks)
8. [Troubleshooting](#troubleshooting)

---

## Performance Overview

The Annotation Swiss Knife includes comprehensive performance infrastructure:

- **Performance Profiling**: Track execution time, memory usage, and detect regressions
- **Streaming Support**: Handle large files without loading into memory
- **Caching**: LRU cache with TTL for frequently accessed data
- **Resource Pooling**: Reuse expensive resources
- **Lazy Loading**: Load services only when needed

---

## Performance Profiling

### Using PerformanceProfiler

**Track execution time and statistics**:

```python
from annotation_toolkit.utils.profiling import PerformanceProfiler

profiler = PerformanceProfiler()

# Context manager profiling
with profiler.profile("operation_name"):
    # Code to profile
    result = expensive_operation()

# Get statistics
stats = profiler.get_statistics("operation_name")
print(f"Calls: {stats['call_count']}")
print(f"Average: {stats['avg_time']:.4f}s")
print(f"Min: {stats['min_time']:.4f}s")
print(f"Max: {stats['max_time']:.4f}s")
print(f"Median: {stats['median']:.4f}s")
print(f"Std Dev: {stats['std_dev']:.4f}s")
print(f"95th %ile: {stats['p95']:.4f}s")
print(f"99th %ile: {stats['p99']:.4f}s")
```

### Decorator-Based Profiling

```python
from annotation_toolkit.utils.profiling import profile_performance

@profile_performance(name="my_function")
def my_function(data):
    # Your code here
    pass

# Automatically profiles every call
result = my_function(large_data)

# View stats
stats = my_function._profiler.get_statistics("my_function")
```

### Memory Profiling

**Requires psutil**:

```python
from annotation_toolkit.utils.profiling import MemoryProfiler, profile_memory

# Decorator-based
@profile_memory(name="memory_intensive")
def load_large_dataset():
    # Your code here
    pass

# Or use directly
mem_profiler = MemoryProfiler()
with mem_profiler.profile("operation"):
    process_large_file()

stats = mem_profiler.get_memory_stats("operation")
print(f"Peak memory: {stats['peak_memory_mb']:.2f} MB")
print(f"Memory delta: {stats['memory_delta_mb']:.2f} MB")
```

### CPU Profiling

```python
from annotation_toolkit.utils.profiling import CPUProfiler

profiler = CPUProfiler()

with profiler.profile("cpu_intensive"):
    # CPU-intensive operation
    complex_computation()

# Save profile for analysis
profiler.save_profile("cpu_intensive", "profile.pstats")

# Analyze with pstats or snakeviz
```

### Regression Detection

```python
from annotation_toolkit.utils.profiling import RegressionDetector

detector = RegressionDetector(threshold_percent=10)

# Compare current performance to baseline
baseline_time = 1.0  # seconds
current_time = 1.15  # seconds

is_regression = detector.check_regression(baseline_time, current_time)
if is_regression:
    print(f"Performance regression detected!")
    print(f"Slowdown: {detector.calculate_slowdown(baseline_time, current_time):.1f}%")
```

### Comprehensive Profiling

```python
from annotation_toolkit.utils.profiling import comprehensive_profile

@comprehensive_profile(name="full_analysis")
def complex_operation(data):
    # Automatically profiles:
    # - Execution time
    # - Memory usage
    # - Call counts
    pass
```

---

## Optimization Techniques

### 1. Streaming for Large Files

**Problem**: Loading large JSON files into memory causes out-of-memory errors

**Solution**: Stream files incrementally

```python
from annotation_toolkit.utils.streaming import StreamingJSONParser

parser = StreamingJSONParser()

# Stream array elements
for item in parser.stream_array("large_conversation.json"):
    # Process each turn individually
    process_turn(item)
    # Memory usage: ~constant

# Stream object key-value pairs
for key, value in parser.stream_object("large_data.json"):
    process_pair(key, value)
```

**When to use**:
- Files > 10MB (configurable: `performance.streaming_threshold_mb`)
- Processing doesn't require entire file in memory
- Memory-constrained environments

**Performance**:
- Memory: O(1) instead of O(n)
- Speed: ~10-20% slower due to incremental parsing
- Trade-off: Worth it for large files

### 2. Caching

**Enable caching** for frequently accessed data:

```yaml
performance:
  enable_caching: true
  cache_ttl_seconds: 300  # 5 minutes
  max_cache_size_mb: 100
```

**Automatic caching**:
- Configuration values
- Tool instances (SINGLETON scope)
- Frequently accessed files

**Manual caching**:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param):
    # Result cached for repeated calls
    return complex_calculation(param)
```

**Cache invalidation**:
```python
expensive_computation.cache_clear()
```

### 3. Resource Pooling

**Reuse expensive resources**:

```python
from annotation_toolkit.utils.resources import ResourcePool

# Create pool
pool = ResourcePool(
    create_resource=lambda: create_database_connection(),
    max_size=10,
    timeout=30.0
)

# Acquire from pool (reuses existing or creates new)
with pool.acquire() as connection:
    result = connection.execute(query)
# Automatically returned to pool
```

**Benefits**:
- Reduces object creation overhead
- Limits concurrent resource usage
- Automatic cleanup

### 4. Lazy Loading

**Don't load tools until needed**:

```python
from annotation_toolkit.di import DIContainer

# Tools resolved lazily
container = bootstrap_application(config)

# Tool only created when first accessed
tool = container.resolve(DictToBulletList)  # Created here
```

**Benefits**:
- Faster startup time
- Lower memory usage
- Only pay for what you use

### 5. Batch Processing

**Process multiple items together**:

```python
# Bad: One at a time
for file in files:
    result = process_file(file)
    save_result(result)  # Many I/O operations

# Good: Batch processing
results = []
for file in files:
    results.append(process_file(file))

# Save all at once
save_batch(results)  # Single I/O operation
```

### 6. Parallel Processing

**Process independent files in parallel**:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# I/O-bound: Use threads
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_file, file_list)

# CPU-bound: Use processes
with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(complex_computation, data_list)
```

**Caution**:
- Ensure operations are thread-safe
- Don't exceed available CPU cores
- Consider memory overhead

---

## Streaming for Large Files

### Automatic Streaming Threshold

```yaml
performance:
  streaming_threshold_mb: 10
```

Files larger than this threshold automatically use streaming.

### Manual Streaming

```python
from annotation_toolkit.utils.streaming import StreamingJSONParser

parser = StreamingJSONParser()

# Chunk-based reading
for chunk in parser.read_in_chunks("huge_file.json", chunk_size=1024*1024):
    # Process 1MB chunks
    process_chunk(chunk)
```

### Streaming Best Practices

**Do**:
- ✅ Use streaming for files > 10MB
- ✅ Process items incrementally
- ✅ Write results incrementally (don't accumulate)
- ✅ Monitor memory usage

**Don't**:
- ❌ Accumulate all results in memory
- ❌ Use streaming for small files (overhead not worth it)
- ❌ Use streaming when you need random access
- ❌ Ignore error handling in streams

---

## Caching Strategies

### LRU Cache with TTL

```yaml
performance:
  enable_caching: true
  cache_ttl_seconds: 300
  max_cache_size: 1000
```

**What's cached**:
- Configuration values
- Tool instances (SINGLETON)
- Validation results (optional)

### Cache Warming

**Pre-load frequently used data**:

```python
def warm_cache():
    # Pre-load configuration
    config.get("tools", "dict_to_bullet", "markdown_output")

    # Pre-load tool instances
    container.resolve(DictToBulletList)
    container.resolve(TextCleaner)
    container.resolve(JsonVisualizer)

# Call at startup
warm_cache()
```

### Cache Monitoring

```python
from annotation_toolkit.utils.profiling import PerformanceProfiler

profiler = PerformanceProfiler()

# Track cache hit rate
with profiler.profile("cache_lookup"):
    result = cached_function(key)

stats = profiler.get_statistics("cache_lookup")
# Low avg_time = high cache hit rate
```

---

## Configuration

### Performance Configuration Options

```yaml
performance:
  # Caching
  enable_caching: true
  cache_ttl_seconds: 300
  max_cache_size: 1000
  max_cache_size_mb: 100

  # Streaming
  streaming_threshold_mb: 10
  stream_chunk_size_kb: 1024

  # Profiling
  enable_profiling: false  # Disable in production
  profiling_sample_rate: 1.0  # 100% of operations

  # Resource pooling
  max_pool_size: 10
  pool_timeout_seconds: 30

  # Parallelism
  max_workers: 4
  use_multiprocessing: false  # false = threads, true = processes
```

### Environment Variables

```bash
export ANNOTATION_TOOLKIT_PERFORMANCE_ENABLE_CACHING=true
export ANNOTATION_TOOLKIT_PERFORMANCE_STREAMING_THRESHOLD_MB=10
export ANNOTATION_TOOLKIT_PERFORMANCE_ENABLE_PROFILING=false
```

---

## Performance Benchmarks

### Baseline Performance

**Dictionary to Bullet List**:
- Small (< 100 items): < 10ms
- Medium (100-1000 items): 10-50ms
- Large (> 1000 items): 50-200ms

**JSON Visualizer**:
- Small JSON (< 1MB): < 50ms
- Medium JSON (1-10MB): 50-500ms
- Large JSON (> 10MB): 500ms-5s (with streaming)

**Text Cleaner**:
- Small text (< 1KB): < 5ms
- Medium text (1-100KB): 5-50ms
- Large text (> 100KB): 50-500ms

**Conversation Generator**:
- Per turn: < 1ms
- 20 turns: < 20ms
- JSON generation: < 10ms

### Memory Usage

**Baseline**:
- CLI: ~30MB
- GUI: ~50-80MB (PyQt5 overhead)

**With large files** (without streaming):
- 10MB JSON: ~80-100MB
- 50MB JSON: ~200-300MB
- 100MB JSON: May fail (OOM)

**With streaming**:
- Any file size: ~constant memory (~50-100MB)

### Optimization Results

**Before optimization**:
- 100MB JSON file: Out of memory
- 1000-item dictionary: 500ms
- 100 conversation turns: 200ms

**After optimization**:
- 100MB JSON file: ~5s (streaming)
- 1000-item dictionary: 50ms (caching)
- 100 conversation turns: 20ms (batch processing)

---

## Troubleshooting

### Slow Performance

**Symptom**: Operations taking longer than expected

**Diagnosis**:
```python
from annotation_toolkit.utils.profiling import profile_performance

@profile_performance(name="slow_operation")
def my_operation():
    # Your code
    pass

# Run and check stats
stats = my_operation._profiler.get_statistics("slow_operation")
print(f"Average time: {stats['avg_time']:.4f}s")
print(f"99th percentile: {stats['p99']:.4f}s")
```

**Solutions**:
1. Enable caching for repeated operations
2. Use streaming for large files
3. Profile to find bottlenecks
4. Consider parallel processing

### High Memory Usage

**Symptom**: Application using too much memory

**Diagnosis**:
```python
from annotation_toolkit.utils.profiling import profile_memory

@profile_memory(name="memory_check")
def my_operation():
    # Your code
    pass

stats = my_operation._memory_profiler.get_memory_stats("memory_check")
print(f"Peak memory: {stats['peak_memory_mb']:.2f} MB")
```

**Solutions**:
1. Use streaming for large files
2. Process in smaller batches
3. Clear caches periodically
4. Reduce max_cache_size

### Performance Regression

**Symptom**: Operation slower than before

**Diagnosis**:
```python
from annotation_toolkit.utils.profiling import RegressionDetector

detector = RegressionDetector(threshold_percent=10)

# Compare to baseline
baseline = 1.0  # Previous average
current = profiler.get_statistics("operation")["avg_time"]

if detector.check_regression(baseline, current):
    print(f"Regression detected: {detector.calculate_slowdown(baseline, current):.1f}% slower")
```

**Solutions**:
1. Profile to identify new bottleneck
2. Check if new feature added overhead
3. Review recent code changes
4. Consider optimization techniques

### Out of Memory

**Symptom**: MemoryError or system slowdown

**Solutions**:
1. **Enable streaming**:
   ```yaml
   performance:
     streaming_threshold_mb: 5  # Lower threshold
   ```

2. **Reduce cache size**:
   ```yaml
   performance:
     max_cache_size_mb: 50  # Smaller cache
   ```

3. **Process in batches**:
   ```python
   batch_size = 100
   for i in range(0, len(items), batch_size):
       batch = items[i:i+batch_size]
       process_batch(batch)
   ```

4. **Use CLI instead of GUI** (lower memory overhead)

---

## Best Practices

### Development

1. **Profile early**: Use profiling during development
2. **Set baselines**: Establish performance baselines for key operations
3. **Monitor regressions**: Detect performance degradations early
4. **Test with large data**: Test with realistic file sizes

### Production

1. **Disable profiling**: `enable_profiling: false`
2. **Enable caching**: `enable_caching: true`
3. **Configure streaming**: Set appropriate `streaming_threshold_mb`
4. **Monitor resources**: Track memory and CPU usage
5. **Tune pool sizes**: Adjust `max_pool_size` based on load

### Optimization Workflow

1. **Measure**: Profile to find bottlenecks
2. **Analyze**: Identify root cause
3. **Optimize**: Apply appropriate technique
4. **Verify**: Re-measure to confirm improvement
5. **Monitor**: Watch for regressions

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [SECURITY.md](SECURITY.md) - Security features
- [CLAUDE.md](../CLAUDE.md) - Developer guidance
- [User_Manual.md](User_Manual.md) - End-user documentation
