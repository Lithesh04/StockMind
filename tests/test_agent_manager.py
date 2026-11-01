from pathlib import Path
from stockmind.agent_manager import StockMindAgent

def test_capstone_agent_perceives_and_optimizes():
    root = Path(__file__).resolve().parents[1]
    agent = StockMindAgent(root / "data" / "inventory.json", root / "data" / "supplier_offers.json")
    scan = agent.perceive_and_reason()
    assert any(item["rule"] == "LOW_STOCK" for item in scan)
    result = agent.optimize_replenishment(50, 60, 7)
    assert result["winner"] is not None

def test_weather_observation_updates_bdi_plan():
    root = Path(__file__).resolve().parents[1]
    agent = StockMindAgent(root / "data" / "inventory.json", root / "data" / "supplier_offers.json")
    agent.perceive_and_reason()
    plan = agent.apply_weather_observation({"delivery_risk": "HIGH"})
    assert "add_delivery_buffer_and_recheck_eta" in plan
