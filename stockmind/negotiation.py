"""Alternating-offer protocol between explicit BuyerAgent and SupplierAgent instances."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BuyerAgent:
    name: str = "StockMind Buyer Agent"
    max_price: float = 52.0
    current_offer: float = 46.0

    def make_offer(self) -> float:
        return round(self.current_offer, 2)

    def respond_to_counter(self, seller_offer: float) -> str:
        if seller_offer <= self.max_price:
            return "ACCEPT"
        self.current_offer = min(self.max_price, self.current_offer + (self.max_price - self.current_offer) * 0.5)
        return "COUNTER"

@dataclass
class SupplierAgent:
    name: str = "Supplier Agent"
    min_price: float = 48.0
    current_ask: float = 54.0

    def respond_to_buyer(self, buyer_offer: float) -> tuple[str, float]:
        if buyer_offer >= self.min_price:
            return "ACCEPT", round(buyer_offer, 2)
        return "COUNTEROFFER", round(self.current_ask, 2)

    def revise_ask(self) -> None:
        self.current_ask = max(self.min_price, self.current_ask - (self.current_ask - self.min_price) * 0.5)


def negotiate(buyer_max: float, supplier_min: float, rounds: int = 6, buyer_start: float | None = None,
              supplier_start: float | None = None) -> dict[str, Any]:
    if buyer_max < supplier_min:
        return {"agreement": False, "timeline": [{"round": 0, "event": "NO_OVERLAP", "buyer_max": buyer_max,
                    "supplier_min": supplier_min}], "agreed_price": None}
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    buyer = BuyerAgent(max_price=float(buyer_max), current_offer=float(buyer_start if buyer_start is not None else buyer_max * 0.86))
    supplier = SupplierAgent(min_price=float(supplier_min), current_ask=float(supplier_start if supplier_start is not None else supplier_min * 1.12))
    timeline = []
    for turn in range(1, rounds + 1):
        buyer_offer = buyer.make_offer()
        timeline.append({"round": turn, "speaker": "BUYER", "offer": buyer_offer})
        response, price = supplier.respond_to_buyer(buyer_offer)
        if response == "ACCEPT":
            timeline.append({"round": turn, "speaker": "SUPPLIER", "response": "ACCEPT", "price": price})
            return {"agreement": True, "agreed_price": price, "timeline": timeline,
                    "buyer_agent": buyer.name, "supplier_agent": supplier.name}
        timeline.append({"round": turn, "speaker": "SUPPLIER", "response": response, "offer": price})
        buyer_response = buyer.respond_to_counter(price)
        if buyer_response == "ACCEPT":
            timeline.append({"round": turn, "speaker": "BUYER", "response": "ACCEPT", "price": price})
            return {"agreement": True, "agreed_price": price, "timeline": timeline,
                    "buyer_agent": buyer.name, "supplier_agent": supplier.name}
        supplier.revise_ask()
    midpoint = round((buyer_max + supplier_min) / 2, 2)
    timeline.append({"round": rounds + 1, "speaker": "SYSTEM", "event": "MEDIATED_AGREEMENT", "price": midpoint})
    return {"agreement": True, "agreed_price": midpoint, "timeline": timeline,
            "buyer_agent": buyer.name, "supplier_agent": supplier.name}
