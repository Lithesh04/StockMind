from stockmind.negotiation import negotiate

def test_negotiation_reaches_agreement_with_overlapping_reservation_prices():
    result = negotiate(52, 48, rounds=6, buyer_start=46, supplier_start=54)
    assert result["agreement"] is True
    assert 48 <= result["agreed_price"] <= 52
    assert len(result["timeline"]) >= 4

def test_no_agreement_when_buyer_limit_below_supplier_minimum():
    result = negotiate(45, 48)
    assert result["agreement"] is False
