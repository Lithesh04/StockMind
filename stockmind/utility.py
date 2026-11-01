"""Constraint filtering and weighted utility ranking for supplier offers."""
from __future__ import annotations
from typing import Any

WEIGHTS = {"cost": 0.40, "delivery": 0.25, "reliability": 0.20, "quality": 0.15}

def score_offer(offer: dict[str, Any], max_unit_budget: float, max_delivery_days: int) -> dict[str, Any]:
    if max_unit_budget <= 0 or max_delivery_days <= 0:
        raise ValueError("Budget and maximum delivery days must be positive")
    price = float(offer["unit_price"])
    delivery_days = int(offer["delivery_days"])
    cost_score = max(0.0, min(100.0, 100.0 * (1.0 - price / max_unit_budget)))
    delivery_score = max(0.0, min(100.0, 100.0 * (1.0 - delivery_days / max_delivery_days)))
    reliability_score = max(0.0, min(100.0, float(offer["reliability_pct"])))
    quality_score = max(0.0, min(100.0, float(offer["quality_rating"]) / 5.0 * 100.0))
    total = (WEIGHTS["cost"] * cost_score + WEIGHTS["delivery"] * delivery_score +
             WEIGHTS["reliability"] * reliability_score + WEIGHTS["quality"] * quality_score)
    return {**offer, "cost_score": round(cost_score, 2), "delivery_score": round(delivery_score, 2),
            "reliability_score": round(reliability_score, 2), "quality_score": round(quality_score, 2),
            "utility_score": round(total, 2)}

def evaluate_offers(offers: list[dict[str, Any]], required_qty: int, max_unit_budget: float,
                    max_delivery_days: int = 7) -> dict[str, Any]:
    evaluated = []
    for offer in offers:
        reasons = []
        if int(offer["available_qty"]) < required_qty:
            reasons.append("insufficient quantity")
        if float(offer["unit_price"]) > max_unit_budget:
            reasons.append("unit price exceeds budget")
        if int(offer["delivery_days"]) > max_delivery_days:
            reasons.append("delivery exceeds limit")
        row = score_offer(offer, max_unit_budget, max_delivery_days)
        row["feasible"] = not reasons
        row["rejection_reasons"] = reasons
        evaluated.append(row)
    feasible = sorted((x for x in evaluated if x["feasible"]), key=lambda x: x["utility_score"], reverse=True)
    return {"evaluated": evaluated, "ranked": feasible, "winner": feasible[0] if feasible else None,
            "feasible_count": len(feasible), "rejected_count": len(evaluated) - len(feasible),
            "weights": WEIGHTS.copy()}

class UtilityOptimizerAgent:
    """Self-interested buyer agent that selects the highest-utility feasible offer."""
    def __init__(self, name: str = "StockMind Buyer Agent"):
        self.name = name
        self.last_result: dict[str, Any] | None = None

    def evaluate(self, offers: list[dict[str, Any]], required_qty: int, max_unit_budget: float,
                 max_delivery_days: int = 7) -> dict[str, Any]:
        self.last_result = evaluate_offers(offers, required_qty, max_unit_budget, max_delivery_days)
        return self.last_result
