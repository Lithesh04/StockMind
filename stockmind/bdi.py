
"""Small Belief-Desire-Intention engine with explicit replanning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BDIEngine:
    beliefs: dict[str, Any] = field(default_factory=dict)
    desires: list[str] = field(default_factory=list)
    intentions: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    def update_belief(self, key: str, value: Any) -> dict[str, Any]:
        old = self.beliefs.get(key)
        self.beliefs[key] = value

        event = {
            "key": key,
            "old": old,
            "new": value
        }

        self.history.append(event)
        return event

    def set_desires(self, desires: list[str]) -> None:
        self.desires = list(desires)

    def replan(self) -> list[str]:
        product = self.beliefs.get("priority_product", "Rice")
        supplier_available = self.beliefs.get(
            "supplier_available", True
        )
        stock = int(self.beliefs.get("current_stock", 0))
        reorder = int(self.beliefs.get("reorder_level", 0))
        weather_risk = self.beliefs.get("delivery_risk", "LOW")

        if stock <= reorder:
            first = (
                "find_alternative_supplier"
                if not supplier_available
                else "request_supplier_quotes"
            )

            plan = [
                first,
                "rank_feasible_offers",
                "negotiate_best_offer",
                "request_human_purchase_approval"
            ]

            # Adapt the plan when weather creates delivery risk.
            if weather_risk in ("MODERATE", "HIGH"):
                plan.insert(
                    1, "add_delivery_buffer_and_recheck_eta"
                )

            # Add another precaution for high weather risk.
            if weather_risk == "HIGH":
                plan.insert(
                    2, "prioritize_weather_resilient_supplier"
                )

        else:
            plan = ["continue_inventory_monitoring"]

        self.intentions = plan

        self.history.append({
            "event": "REPLAN",
            "product": product,
            "weather_risk": weather_risk,
            "intentions": plan.copy()
        })

        return plan

    def snapshot(self) -> dict[str, Any]:
        return {
            "beliefs": self.beliefs.copy(),
            "desires": self.desires.copy(),
            "intentions": self.intentions.copy(),
            "history": self.history.copy()
        }
