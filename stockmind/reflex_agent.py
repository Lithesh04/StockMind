"""Simple condition-action agent for inventory telemetry."""
from __future__ import annotations
from typing import Any

class ReflexAgent:
    """Maps current percepts directly to actions; no long-term planning."""
    def evaluate(self, product: dict[str, Any]) -> dict[str, Any]:
        stock = int(product["current_stock"])
        reorder = int(product["reorder_level"])
        target = int(product["target_stock"])
        if stock == 0:
            rule, action, severity = "ZERO_STOCK", "URGENT_REPLENISHMENT", "CRITICAL"
        elif stock <= reorder:
            rule, action, severity = "LOW_STOCK", "CREATE_REPLENISHMENT_REQUEST", "WARNING"
        elif stock > target:
            rule, action, severity = "OVERSTOCK", "REVIEW_EXCESS_INVENTORY", "INFO"
        else:
            rule, action, severity = "STOCK_NORMAL", "CONTINUE_MONITORING", "OK"
        quantity = max(0, target - stock) if action in {"URGENT_REPLENISHMENT", "CREATE_REPLENISHMENT_REQUEST"} else 0
        return {
            "sku": product["sku"], "product": product["product"], "stock": stock,
            "reorder_level": reorder, "target_stock": target, "rule": rule,
            "action": action, "severity": severity, "reorder_quantity": quantity,
        }

    def scan(self, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.evaluate(product) for product in products]
