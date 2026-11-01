"""Ed25519 signed message envelopes with trusted-key and replay checks."""
from __future__ import annotations
import base64
import json
import time
import uuid
from pathlib import Path
from typing import Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical_bytes(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def ensure_demo_keys(key_dir: str | Path) -> dict[str, str]:
    folder = Path(key_dir)
    folder.mkdir(parents=True, exist_ok=True)
    result = {}
    for name in ("buyer", "supplier"):
        private_path = folder / f"{name}_private.pem"
        public_path = folder / f"{name}_public.pem"
        if not private_path.exists() or not public_path.exists():
            private_key = Ed25519PrivateKey.generate()
            private_path.write_bytes(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()))
            public_path.write_bytes(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo))
        result[name] = str(private_path)
    return result


def create_signed_envelope(sender: str, payload: dict[str, Any], private_key_path: str | Path) -> dict[str, Any]:
    body = {"sender": sender, "payload": payload, "timestamp": int(time.time()), "nonce": uuid.uuid4().hex}
    private_key = serialization.load_pem_private_key(Path(private_key_path).read_bytes(), password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("Expected an Ed25519 private key")
    signature = private_key.sign(canonical_bytes(body))
    return {**body, "signature": base64.b64encode(signature).decode("ascii")}


def verify_envelope(envelope: dict[str, Any], trusted_public_keys: dict[str, str | Path],
                    seen_nonces: set[str] | None = None, max_age_seconds: int = 300) -> tuple[bool, str]:
    sender = envelope.get("sender")
    if sender not in trusted_public_keys:
        return False, "UNTRUSTED_SENDER"
    required = {"sender", "payload", "timestamp", "nonce", "signature"}
    if not required.issubset(envelope):
        return False, "MISSING_FIELDS"
    try:
        timestamp = int(envelope["timestamp"])
        if abs(int(time.time()) - timestamp) > max_age_seconds:
            return False, "EXPIRED_TIMESTAMP"
        nonce = str(envelope["nonce"])
        if seen_nonces is not None and nonce in seen_nonces:
            return False, "REPLAYED_NONCE"
        body = {key: envelope[key] for key in ("sender", "payload", "timestamp", "nonce")}
        public_key = serialization.load_pem_public_key(Path(trusted_public_keys[sender]).read_bytes())
        if not isinstance(public_key, Ed25519PublicKey):
            return False, "INVALID_PUBLIC_KEY_TYPE"
        public_key.verify(base64.b64decode(envelope["signature"], validate=True), canonical_bytes(body))
        if seen_nonces is not None:
            seen_nonces.add(nonce)
        return True, "VERIFIED"
    except Exception:
        return False, "INVALID_SIGNATURE_OR_FORMAT"
