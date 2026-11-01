"""Start Supplier Agent B. Run this in terminal 1."""
from pathlib import Path
from stockmind.security import ensure_demo_keys
from stockmind.socket_server import serve_supplier

ROOT = Path(__file__).resolve().parent
ensure_demo_keys(ROOT / "data" / "keys")
serve_supplier(root=ROOT)
