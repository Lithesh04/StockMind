"""Generate local demo keys and initialize StockMind's local data files."""
from pathlib import Path
from stockmind.security import ensure_demo_keys
from stockmind.database import EventStore
ROOT = Path(__file__).resolve().parent
ensure_demo_keys(ROOT / "data" / "keys")
EventStore(ROOT / "data" / "stockmind.db")
print("StockMind setup complete. Demo keys and SQLite event store are ready.")
