"""Newline-delimited JSON transport helpers for TCP socket messages."""
from __future__ import annotations
import json
import socket
from typing import Any

def send_json_line(sock: socket.socket, message: dict[str, Any]) -> None:
    encoded = json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"
    sock.sendall(encoded)

def receive_json_line(sock: socket.socket, max_bytes: int = 1_000_000) -> dict[str, Any]:
    chunks = bytearray()
    while len(chunks) <= max_bytes:
        part = sock.recv(1)
        if not part:
            break
        if part == b"\n":
            break
        chunks.extend(part)
    if not chunks:
        raise ConnectionError("Peer closed the connection before sending a message")
    if len(chunks) > max_bytes:
        raise ValueError("Message exceeds configured size limit")
    parsed = json.loads(chunks.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Message must be a JSON object")
    return parsed
