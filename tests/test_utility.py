from stockmind.demo import load_offers
from stockmind.utility import evaluate_offers

def test_ten_offers_are_evaluated_and_winner_is_feasible():
    result = evaluate_offers(load_offers(), required_qty=50, max_unit_budget=60, max_delivery_days=7)
    assert len(result["evaluated"]) == 10
    assert result["winner"] is not None
    assert result["winner"]["feasible"] is True
    assert result["winner"]["available_qty"] >= 50
