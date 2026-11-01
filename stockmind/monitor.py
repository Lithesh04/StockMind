"""Threaded inventory monitor with a thread-safe queue and clean shutdown."""
from __future__ import annotations
import queue
import threading
import time
from typing import Callable, Any

class InventoryMonitor:
    def __init__(self, inventory_provider: Callable[[], list[dict[str, Any]]], interval_seconds: float = 5.0):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self.inventory_provider = inventory_provider
        self.interval_seconds = interval_seconds
        self.events: queue.Queue[dict[str, Any]] = queue.Queue()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.scan_count = 0

    def _run(self) -> None:
        while not self.stop_event.is_set():
            started = time.perf_counter()
            try:
                snapshot = self.inventory_provider()
                self.events.put({"type": "INVENTORY_SNAPSHOT", "items": snapshot, "scan": self.scan_count + 1,
                                 "latency_ms": (time.perf_counter() - started) * 1000})
                self.scan_count += 1
            except Exception as exc:  # keep the worker alive and report failures
                self.events.put({"type": "MONITOR_ERROR", "error": str(exc)})
            self.stop_event.wait(self.interval_seconds)

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, name="stockmind-monitor", daemon=True)
        self.thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=timeout)

    def read_events(self) -> list[dict[str, Any]]:
        results = []
        while True:
            try:
                results.append(self.events.get_nowait())
            except queue.Empty:
                break
        return results
