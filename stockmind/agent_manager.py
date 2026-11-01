"""Capstone orchestrator that connects perception, BDI, utility and recommendations."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .environment import InventoryEnvironment
from .reflex_agent import ReflexAgent
from .bdi import BDIEngine
from .utility import UtilityOptimizerAgent

class StockMindAgent:
    """The main buyer agent coordinating the modular reasoning components."""
    def __init__(self, inventory_path: str | Path | None = None, offers_path: str | Path | None = None):
        self.environment = InventoryEnvironment(inventory_path)
        self.reflex = ReflexAgent()
        self.bdi = BDIEngine(desires=["avoid_stockout", "minimize_replenishment_cost", "maintain_supplier_reliability"])
        self.optimizer = UtilityOptimizerAgent()
        self.offers_path = Path(offers_path) if offers_path else Path(__file__).resolve().parents[1] / "data" / "supplier_offers.json"
        self.last_scan: list[dict[str, Any]] = []
        self.last_optimization: dict[str, Any] | None = None

    def perceive_and_reason(self) -> list[dict[str, Any]]:
        products = self.environment.list_products()
        self.last_scan = self.reflex.scan(products)
        priority = next((item for item in self.last_scan if item["reorder_quantity"] > 0), None)
        if priority:
            original = self.environment.get_product(priority["sku"])
            self.bdi.update_belief("priority_product", original["product"])
            self.bdi.update_belief("current_stock", original["current_stock"])
            self.bdi.update_belief("reorder_level", original["reorder_level"])
            self.bdi.replan()
        return self.last_scan

    def optimize_replenishment(self, required_qty: int, max_unit_budget: float = 60.0,
                               max_delivery_days: int = 7) -> dict[str, Any]:
        offers = json.loads(self.offers_path.read_text(encoding="utf-8"))
        self.last_optimization = self.optimizer.evaluate(offers, required_qty, max_unit_budget, max_delivery_days)
        return self.last_optimization

    def apply_weather_observation(self, weather: dict[str, Any]) -> list[str]:
        risk = str(weather.get("delivery_risk", "LOW")).upper()
        self.bdi.update_belief("delivery_risk", risk)
        return self.bdi.replan()

    def update_supplier_availability(self, available: bool) -> list[str]:
        self.bdi.update_belief("supplier_available", bool(available))
        return self.bdi.replan()

    def dashboard_snapshot(self) -> dict[str, Any]:
        return {"agent": "StockMind", "inventory": self.environment.list_products(),
                "reflex_scan": self.last_scan, "bdi": self.bdi.snapshot(),
                "last_optimization": self.last_optimization}
