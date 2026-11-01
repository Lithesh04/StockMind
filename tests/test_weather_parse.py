from stockmind.weather_api import parse_weather_payload

def test_weather_payload_is_parsed_into_delivery_risk():
    payload = {"timezone": "Asia/Kolkata", "hourly": {
        "time": ["2026-01-01T00:00", "2026-01-01T01:00"],
        "precipitation_probability": [10, 85], "precipitation": [0, 2.5]}}
    result = parse_weather_payload(payload)
    assert result["delivery_risk"] == "HIGH"
    assert result["max_precipitation_probability_pct"] == 85
