"""StockMind buyer TCP client. Run with: python run_buyer.py"""
from __future__ import annotations
import socket
from pathlib import Path
from typing import Any
from .protocol import receive_json_line, send_json_line
from .security import create_signed_envelope, verify_envelope

def request_supplier_quote(product: str, quantity: int, budget: float, host: str = "127.0.0.1",
                           port: int = 5055, root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    key_dir = root / "data" / "keys"
    envelope = create_signed_envelope("STOCKMIND_BUYER", {
        "message_type": "RESTOCK_REQUEST", "product": product, "quantity": quantity,
        "max_unit_budget": budget
    }, key_dir / "buyer_private.pem")
    with socket.create_connection((host, port), timeout=8) as sock:
        send_json_line(sock, envelope)
        response = receive_json_line(sock)
    if response.get("status") == "REJECTED":
        raise PermissionError(f"Supplier rejected request: {response.get('reason')}")
    ok, reason = verify_envelope(response, {"SUPPLIER_AGENT": key_dir / "supplier_public.pem"}, set())
    if not ok:
        raise PermissionError(f"Supplier response failed authentication: {reason}")
    return response["payload"]
