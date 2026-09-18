"""Lightweight per-stage profiler for the frame pipeline.

Enable with the environment variable ``VISOMASTER_PROFILE=1`` (or ``true``/``yes``).
When disabled (default) every timer is a no-op, so there is no runtime overhead.

Stages are reported every ``REPORT_EVERY`` processed frames and once more when
processing stops. Timings are accumulated across worker threads under a lock.
"""

import os
import threading
import time
from collections import defaultdict
from functools import wraps

ENABLED = os.environ.get("VISOMASTER_PROFILE", "").strip().lower() in ("1", "true", "yes", "on")

REPORT_EVERY = 60

_lock = threading.Lock()
_stats: dict[str, list] = defaultdict(lambda: [0.0, 0])
_frames = 0


class timer:
    """Context manager that accumulates elapsed time under ``name``."""

    __slots__ = ("name", "_t0")

    def __init__(self, name: str):
        self.name = name
        self._t0 = 0.0

    def __enter__(self):
        if ENABLED:
            self._t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        if ENABLED:
            dt = time.perf_counter() - self._t0
            with _lock:
                entry = _stats[self.name]
                entry[0] += dt
                entry[1] += 1
        return False


def wrap(fn, name: str):
    """Return a timing wrapper around ``fn`` (used to instrument bound methods)."""
    if not ENABLED:
        return fn

    @wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt = time.perf_counter() - t0
            with _lock:
                entry = _stats[name]
                entry[0] += dt
                entry[1] += 1

    return wrapper


def _format_stats_locked() -> str:
    if not _stats and _frames == 0:
        return ""
    lines = [f"--- profile (frames={_frames}) ---"]
    for name, (total, count) in sorted(_stats.items(), key=lambda kv: -kv[1][0]):
        lines.append(f"  {name:30} {total * 1000 / count:8.2f} ms x{count}")
    return "\n".join(lines)


def frame_done():
    """Call once per processed frame; prints a report every REPORT_EVERY frames."""
    if not ENABLED:
        return
    global _frames
    with _lock:
        _frames += 1
        if _frames % REPORT_EVERY == 0:
            print(_format_stats_locked(), flush=True)


def report_and_reset():
    """Print the accumulated report and clear the counters."""
    if not ENABLED:
        return
    global _frames
    with _lock:
        text = _format_stats_locked()
        _stats.clear()
        _frames = 0
    if text:
        print(text, flush=True)
