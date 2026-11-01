"""Supplier TCP server. Run with: python run_supplier.py"""
from __future__ import annotations
import json
import socketserver
from pathlib import Path
from typing import Any
from .protocol import receive_json_line, send_json_line
from .security import create_signed_envelope, verify_envelope

class _ReusableServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve_supplier(host: str = "127.0.0.1", port: int = 5055, root: str | Path = ".") -> None:
    root = Path(root)
    key_dir = root / "data" / "keys"
    buyer_public = key_dir / "buyer_public.pem"
    supplier_private = key_dir / "supplier_private.pem"
    seen_nonces: set[str] = set()
    trusted = {"STOCKMIND_BUYER": buyer_public}

    class Handler(socketserver.BaseRequestHandler):
        def handle(self) -> None:
            try:
                envelope = receive_json_line(self.request)
                ok, reason = verify_envelope(envelope, trusted, seen_nonces)
                if not ok:
                    print(f"[SECURITY] Request rejected: {reason}", flush=True)
                    send_json_line(self.request, {"status": "REJECTED", "reason": reason})
                    return
                payload = envelope["payload"]
                print(f"[SUPPLIER] Authenticated request from {envelope['sender']}: {payload}", flush=True)
                quantity = int(payload.get("quantity", 0))
                # Demonstration quote: this is simulated supplier inventory and pricing.
                quote_payload: dict[str, Any] = {
                    "message_type": "SUPPLIER_QUOTE", "supplier": "SUPPLIER_AGENT",
                    "product": payload.get("product", "Unknown"), "quantity": quantity,
                    "unit_price": 49.50, "available_qty": 500, "delivery_days": 2,
                    "reliability_pct": 94, "quality_rating": 4.5,
                    "note": "Simulated supplier quote for academic demonstration"
                }
                response = create_signed_envelope("SUPPLIER_AGENT", quote_payload, supplier_private)
                send_json_line(self.request, response)
                print("[SUPPLIER] Signed quote sent", flush=True)
            except Exception as exc:
                print(f"[SUPPLIER] Error: {exc}", flush=True)

    with _ReusableServer((host, port), Handler) as server:
        print(f"[SUPPLIER] Listening on {host}:{port}", flush=True)
        print("[SUPPLIER] Press Ctrl+C to stop", flush=True)
        try:
            server.serve_forever(poll_interval=0.25)
        except KeyboardInterrupt:
            print("[SUPPLIER] Shutting down", flush=True)
