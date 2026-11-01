from stockmind.bdi import BDIEngine

def test_intention_changes_when_supplier_becomes_unavailable():
    agent = BDIEngine(beliefs={"current_stock": 5, "reorder_level": 10, "supplier_available": True})
    first = agent.replan()
    agent.update_belief("supplier_available", False)
    second = agent.replan()
    assert first != second
    assert second[0] == "find_alternative_supplier"
