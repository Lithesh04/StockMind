"""Run StockMind Buyer Agent A. Start run_supplier.py first in another terminal."""
from pathlib import Path
from stockmind.security import ensure_demo_keys
from stockmind.socket_client import request_supplier_quote

ROOT = Path(__file__).resolve().parent
ensure_demo_keys(ROOT / "data" / "keys")

if __name__ == "__main__":
    print("[BUYER] Sending signed RESTOCK_REQUEST to Supplier Agent...")
    quote = request_supplier_quote("Milk", 92, 60.0, root=ROOT)
    print("[BUYER] Supplier response signature verified")
    print("[BUYER] Quote received:")
    for key, value in quote.items():
        print(f"  {key}: {value}")
