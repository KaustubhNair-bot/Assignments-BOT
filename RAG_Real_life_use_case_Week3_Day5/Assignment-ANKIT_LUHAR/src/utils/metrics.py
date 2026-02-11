"""
DP World RAG Chatbot — Custom Metrics.

Simple in-memory metrics collection for monitoring.
"""

from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Lock
from typing import Generator


@dataclass
class MetricsSummary:
    """Summary statistics for a metric."""

    count: int = 0
    total: float = 0.0
    min_val: float = float("inf")
    max_val: float = 0.0

    @property
    def avg(self) -> float:
        return self.total / max(self.count, 1)

    def record(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.min_val = min(self.min_val, value)
        self.max_val = max(self.max_val, value)


class MetricsCollector:
    """Lightweight in-memory metrics collector."""

    _instance: MetricsCollector | None = None
    _lock = Lock()

    def __new__(cls) -> MetricsCollector:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._counters: dict[str, int] = defaultdict(int)
                    cls._instance._timers: dict[str, MetricsSummary] = defaultdict(MetricsSummary)
        return cls._instance

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        with self._lock:
            self._counters[name] += value

    def record_time(self, name: str, duration: float) -> None:
        """Record a timing measurement."""
        with self._lock:
            self._timers[name].record(duration)

    @contextmanager
    def timer(self, name: str) -> Generator[None, None, None]:
        """Context manager to time a block of code."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.record_time(name, duration)

    def get_stats(self) -> dict:
        """Return all metrics as a dict."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timers": {
                    name: {
                        "count": s.count,
                        "avg_ms": round(s.avg * 1000, 2),
                        "min_ms": round(s.min_val * 1000, 2) if s.min_val != float("inf") else 0,
                        "max_ms": round(s.max_val * 1000, 2),
                        "total_ms": round(s.total * 1000, 2),
                    }
                    for name, s in self._timers.items()
                },
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._timers.clear()
