import time
from stockmind.monitor import InventoryMonitor

def test_monitor_emits_events_and_stops():
    monitor = InventoryMonitor(lambda: [{"sku": "X"}], interval_seconds=0.05)
    monitor.start()
    time.sleep(0.13)
    monitor.stop()
    events = monitor.read_events()
    assert len(events) >= 1
    assert events[0]["type"] == "INVENTORY_SNAPSHOT"
    assert events[0]["latency_ms"] >= 0
