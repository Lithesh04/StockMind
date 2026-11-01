from pathlib import Path
from stockmind.security import ensure_demo_keys, create_signed_envelope, verify_envelope

def test_valid_signature_unknown_sender_and_tampering(tmp_path: Path):
    keys = ensure_demo_keys(tmp_path)
    trusted = {"STOCKMIND_BUYER": tmp_path / "buyer_public.pem"}
    msg = create_signed_envelope("STOCKMIND_BUYER", {"command": "RESTOCK"}, keys["buyer"])
    assert verify_envelope(msg, trusted, set())[0] is True
    bad = create_signed_envelope("STOCKMIND_BUYER", {"command": "RESTOCK"}, keys["buyer"])
    bad["payload"]["command"] = "DELETE_ALL"
    assert verify_envelope(bad, trusted, set())[0] is False
    unknown = create_signed_envelope("UNKNOWN", {"command": "RESTOCK"}, keys["supplier"])
    assert verify_envelope(unknown, trusted, set()) == (False, "UNTRUSTED_SENDER")

def test_replayed_nonce_is_rejected(tmp_path: Path):
    keys = ensure_demo_keys(tmp_path)
    trusted = {"STOCKMIND_BUYER": tmp_path / "buyer_public.pem"}
    msg = create_signed_envelope("STOCKMIND_BUYER", {"command": "RESTOCK"}, keys["buyer"])
    seen = set()
    assert verify_envelope(msg, trusted, seen)[0] is True
    assert verify_envelope(msg, trusted, seen) == (False, "REPLAYED_NONCE")
