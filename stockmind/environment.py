"""Simulated warehouse environment and inventory state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_INVENTORY = [
    {"sku": "RICE-001", "product": "Rice", "current_stock": 15, "reorder_level": 20, "target_stock": 100, "unit": "kg", "unit_cost": 58, "category": "Grocery"},
    {"sku": "MILK-001", "product": "Milk", "current_stock": 8, "reorder_level": 25, "target_stock": 100, "unit": "litres", "unit_cost": 48, "category": "Dairy"},
    {"sku": "SUGAR-001", "product": "Sugar", "current_stock": 60, "reorder_level": 20, "target_stock": 100, "unit": "kg", "unit_cost": 44, "category": "Grocery"},
    {"sku": "OIL-001", "product": "Cooking Oil", "current_stock": 12, "reorder_level": 15, "target_stock": 80, "unit": "litres", "unit_cost": 135, "category": "Grocery"},
    {"sku": "BISC-001", "product": "Biscuits", "current_stock": 45, "reorder_level": 15, "target_stock": 80, "unit": "packs", "unit_cost": 10, "category": "Snacks"},
]

class InventoryEnvironment:
    """A small, observable-in-part warehouse simulation."""
    def __init__(self, inventory_path: str | Path | None = None):
        self.inventory_path = Path(inventory_path) if inventory_path else None
        self.products: list[dict[str, Any]] = []
        if self.inventory_path and self.inventory_path.exists():
            self.load()
        else:
            self.products = [item.copy() for item in DEFAULT_INVENTORY]

    def load(self) -> None:
        if not self.inventory_path:
            return
        self.products = json.loads(self.inventory_path.read_text(encoding="utf-8"))

    def save(self) -> None:
        if self.inventory_path:
            self.inventory_path.parent.mkdir(parents=True, exist_ok=True)
            self.inventory_path.write_text(json.dumps(self.products, indent=2), encoding="utf-8")

    def list_products(self) -> list[dict[str, Any]]:
        return [item.copy() for item in self.products]

    def get_product(self, sku: str) -> dict[str, Any]:
        for item in self.products:
            if item["sku"] == sku:
                return item
        raise KeyError(f"Unknown SKU: {sku}")

    def update_stock(self, sku: str, new_stock: int) -> dict[str, Any]:
        if new_stock < 0:
            raise ValueError("Stock cannot be negative")
        product = self.get_product(sku)
        old_stock = product["current_stock"]
        product["current_stock"] = int(new_stock)
        self.save()
        return {"sku": sku, "product": product["product"], "old_stock": old_stock, "new_stock": int(new_stock)}

    def simulate_sale(self, sku: str, quantity: int) -> dict[str, Any]:
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        product = self.get_product(sku)
        return self.update_stock(sku, max(0, product["current_stock"] - quantity))
