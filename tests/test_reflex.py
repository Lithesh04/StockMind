from stockmind.reflex_agent import ReflexAgent

def test_low_stock_triggers_replenishment():
    product = {"sku": "X", "product": "Test", "current_stock": 4, "reorder_level": 5, "target_stock": 20}
    result = ReflexAgent().evaluate(product)
    assert result["rule"] == "LOW_STOCK"
    assert result["reorder_quantity"] == 16

def test_normal_stock_does_not_reorder():
    product = {"sku": "X", "product": "Test", "current_stock": 10, "reorder_level": 5, "target_stock": 20}
    result = ReflexAgent().evaluate(product)
    assert result["action"] == "CONTINUE_MONITORING"
