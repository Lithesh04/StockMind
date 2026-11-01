"""Reusable assignment demonstrations and deterministic end-to-end demo."""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any
from .environment import InventoryEnvironment
from .reflex_agent import ReflexAgent
from .monitor import InventoryMonitor
from .utility import evaluate_offers
from .negotiation import negotiate
from .bdi import BDIEngine
from .security import ensure_demo_keys, create_signed_envelope, verify_envelope
from .weather_api import fetch_weather
from .agent_manager import StockMindAgent

ROOT = Path(__file__).resolve().parents[1]

def load_offers() -> list[dict[str, Any]]:
    return json.loads((ROOT / "data" / "supplier_offers.json").read_text(encoding="utf-8"))

def run_reflex_demo() -> str:
    env = InventoryEnvironment(ROOT / "data" / "inventory.json")
    agent = ReflexAgent()
    lines = ["ASSIGNMENT 1.2 - RULE-BASED ENVIRONMENTAL REASONER", "=" * 55]
    for result in agent.scan(env.list_products()):
        lines.append(f"[SENSE] {result['product']}: stock={result['stock']} / reorder={result['reorder_level']}")
        lines.append(f"[RULE] {result['rule']} -> [ACTION] {result['action']}")
        if result["reorder_quantity"]:
            lines.append(f"[REORDER] {result['reorder_quantity']} {env.get_product(result['sku'])['unit']} requested")
    return "\n".join(lines)

def run_monitor_demo(duration_seconds: float = 1.2) -> str:
    env = InventoryEnvironment(ROOT / "data" / "inventory.json")
    monitor = InventoryMonitor(env.list_products, interval_seconds=0.3)
    lines = ["ASSIGNMENT 2.1 - CONCURRENT BACKGROUND MONITOR", "=" * 55]
    monitor.start()
    time.sleep(duration_seconds)
    monitor.stop()
    events = monitor.read_events()
    for event in events:
        if event["type"] == "INVENTORY_SNAPSHOT":
            lines.append(f"[WORKER] scan={event['scan']} items={len(event['items'])} latency={event['latency_ms']:.3f} ms")
        else:
            lines.append(f"[WORKER ERROR] {event['error']}")
    lines.append("[MAIN] Main process continued while daemon worker polled inventory")
    return "\n".join(lines)

def run_negotiation_demo() -> str:
    result = negotiate(buyer_max=52.0, supplier_min=48.0, rounds=6, buyer_start=46.0, supplier_start=54.0)
    lines = ["ASSIGNMENT 3.1 - BUYER / SUPPLIER NEGOTIATION", "=" * 55]
    for item in result["timeline"]:
        if item.get("response") == "COUNTEROFFER":
            lines.append(f"[ROUND {item['round']}] SUPPLIER counteroffers INR {item['offer']:.2f}")
        elif item.get("response") == "ACCEPT":
            lines.append(f"[ROUND {item['round']}] {item['speaker']} ACCEPTS INR {item['price']:.2f}")
        elif "offer" in item:
            lines.append(f"[ROUND {item['round']}] {item['speaker']} proposes INR {item['offer']:.2f}")
        else:
            lines.append(f"[ROUND {item['round']}] {item.get('event')}: INR {item.get('price', '')}")
    lines.append(f"[RESULT] Agreement={result['agreement']} | Unit price=INR {result['agreed_price']}")
    return "\n".join(lines)

def run_utility_demo() -> tuple[str, dict[str, Any]]:
    result = evaluate_offers(load_offers(), required_qty=50, max_unit_budget=60.0, max_delivery_days=7)
    lines = ["ASSIGNMENT 3.2 - UTILITY OPTIMIZATION", "=" * 55,
             "U = 0.40*Cost + 0.25*Delivery + 0.20*Reliability + 0.15*Quality",
             "Hard constraints: quantity >= 50, unit price <= INR 60, delivery <= 7 days", ""]
    for row in sorted(result["evaluated"], key=lambda x: x["utility_score"], reverse=True):
        status = "FEASIBLE" if row["feasible"] else "REJECTED: " + ", ".join(row["rejection_reasons"])
        lines.append(f"{row['supplier']:<14} utility={row['utility_score']:>6.2f} | {status}")
    if result["winner"]:
        lines += ["", f"[WINNER] {result['winner']['supplier']}", f"[UTILITY] {result['winner']['utility_score']:.2f}/100",
                  f"[OFFER] INR {result['winner']['unit_price']:.2f}/unit, {result['winner']['delivery_days']} days"]
    else:
        lines.append("[NO FEASIBLE OFFER]")
    return "\n".join(lines), result


def run_bdi_demo():
    bdi = BDIEngine(
        beliefs={
            "priority_product": "Rice",
            "current_stock": 15,
            "reorder_level": 20,
            "supplier_available": True,
            "delivery_risk": "LOW"
        },
        desires=[
            "avoid_stockout",
            "minimize_replenishment_cost"
        ]
    )

    # Store the initial beliefs before the event
    initial_beliefs = bdi.beliefs.copy()

    # Generate the first plan
    initial = bdi.replan()

    # Simulate an unexpected supplier failure
    event = bdi.update_belief(
        "supplier_available", False
    )

    # Store updated beliefs
    updated_beliefs = bdi.beliefs.copy()

    # Recalculate the plan
    changed = bdi.replan()

    lines = [
        "ASSIGNMENT 4.1 - BDI INTENTION CHANGE",
        "=" * 55,
        f"[INITIAL BELIEFS] {initial_beliefs}",
        f"[DESIRES] {bdi.desires}",
        f"[INITIAL INTENTIONS] {initial}",
        "[EVENT] Supplier A becomes unavailable",
        f"[BELIEF UPDATE] {event['old']} -> {event['new']}",
        f"[UPDATED BELIEFS] {updated_beliefs}",
        f"[REPLANNED INTENTIONS] {changed}",
        f"[VERIFICATION] Belief changed: {event['old'] != event['new']}",
        f"[VERIFICATION] Intention changed: {initial != changed}"
    ]

    return "\n".join(lines)


def run_security_demo() -> str:
    key_dir = ROOT / "data" / "keys"
    keys = ensure_demo_keys(key_dir)
    trusted = {"STOCKMIND_BUYER": key_dir / "buyer_public.pem"}
    valid = create_signed_envelope("STOCKMIND_BUYER", {"command": "REQUEST_QUOTE", "product": "Rice"}, keys["buyer"])
    seen: set[str] = set()
    ok, reason = verify_envelope(valid, trusted, seen)
    replay_ok, replay_reason = verify_envelope(valid, trusted, seen)
    tampered = create_signed_envelope("STOCKMIND_BUYER", {"command": "REQUEST_QUOTE", "product": "Milk"}, keys["buyer"])
    tampered["payload"]["product"] = "Gold"
    tamper_ok, tamper_reason = verify_envelope(tampered, trusted, set())
    unknown = create_signed_envelope("UNKNOWN_HOST", {"command": "DELETE_INVENTORY"}, keys["supplier"])
    unknown_ok, unknown_reason = verify_envelope(unknown, trusted, set())
    return "\n".join(["ASSIGNMENT 5.1 - MESSAGE AUTHENTICATION", "=" * 55,
        f"[TRUSTED SIGNED MESSAGE] accepted={ok} reason={reason}",
        f"[REPLAY TEST] accepted={replay_ok} reason={replay_reason}",
        f"[TAMPER TEST] accepted={tamper_ok} reason={tamper_reason}",
        f"[UNKNOWN SENDER] accepted={unknown_ok} reason={unknown_reason}"])

def run_api_demo(latitude: float = 13.0827, longitude: float = 80.2707) -> dict[str, Any]:
    return fetch_weather(latitude, longitude)

def run_capstone_integration_demo() -> str:
    agent = StockMindAgent(ROOT / "data" / "inventory.json", ROOT / "data" / "supplier_offers.json")
    scan = agent.perceive_and_reason()
    flagged = [item["product"] for item in scan if item["reorder_quantity"] > 0]
    optimization = agent.optimize_replenishment(required_qty=50, max_unit_budget=60.0, max_delivery_days=7)
    old_plan = agent.bdi.intentions.copy()
    new_plan = agent.update_supplier_availability(False)
    winner = optimization["winner"]["supplier"] if optimization["winner"] else "None"
    return "\n".join(["ASSIGNMENT 5.2 - CAPSTONE AGENT INTEGRATION", "=" * 55,
        f"[PERCEPTION] Low-stock products: {', '.join(flagged)}",
        f"[PLANNING] Initial intentions: {old_plan}",
        f"[OPTIMIZATION] Best feasible supplier: {winner}",
        f"[BELIEF UPDATE] Supplier availability changed to False",
        f"[REPLANNING] Active intentions: {new_plan}",
        "[CAPSTONE STATUS] Main agent connected perception, BDI and utility modules"])

def run_all_demos(include_live_api: bool = False) -> dict[str, Any]:
    sections: list[str] = [run_reflex_demo(), run_monitor_demo(), run_negotiation_demo(), run_capstone_integration_demo()]
    utility_text, utility_result = run_utility_demo()
    sections.extend([utility_text, run_bdi_demo(), run_security_demo()])
    if include_live_api:
        try:
            weather = run_api_demo()
            sections.append("ASSIGNMENT 4.2 - LIVE OPEN-METEO API\n" + json.dumps(weather, indent=2))
        except Exception as exc:
            weather = {"status": "unavailable", "error": str(exc)}
            sections.append("ASSIGNMENT 4.2 - LIVE API NOT AVAILABLE\n" + str(exc))
    else:
        weather = {"status": "not_requested", "hint": "Run python main.py api to fetch a live forecast."}
    return {"text": "\n\n".join(sections), "utility": utility_result, "weather": weather}
