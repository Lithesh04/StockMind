"""Open-Meteo integration. Weather is used as a configurable delivery-risk signal."""
from __future__ import annotations
import requests
from typing import Any

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def parse_weather_payload(payload: dict[str, Any]) -> dict[str, Any]:
    hourly = payload.get("hourly", {})
    probabilities = hourly.get("precipitation_probability", [])
    precipitation = hourly.get("precipitation", [])
    times = hourly.get("time", [])
    if not probabilities and not precipitation:
        raise ValueError("Weather response did not contain precipitation values")
    probability_values = [float(x) for x in probabilities if x is not None]
    precipitation_values = [float(x) for x in precipitation if x is not None]
    max_probability = max(probability_values) if probability_values else 0.0
    max_precipitation = max(precipitation_values) if precipitation_values else 0.0
    risk = "HIGH" if max_probability >= 70 or max_precipitation >= 5 else "MODERATE" if max_probability >= 40 or max_precipitation >= 1 else "LOW"
    return {"source": "Open-Meteo", "timezone": payload.get("timezone", "unknown"),
            "hours_returned": len(times), "max_precipitation_probability_pct": max_probability,
            "max_hourly_precipitation_mm": max_precipitation, "delivery_risk": risk}

def fetch_weather(latitude: float, longitude: float, timeout: int = 12) -> dict[str, Any]:
    params = {"latitude": latitude, "longitude": longitude,
              "hourly": "precipitation_probability,precipitation", "forecast_days": 1, "timezone": "auto"}
    response = requests.get(OPEN_METEO_URL, params=params, timeout=timeout)
    response.raise_for_status()
    result = parse_weather_payload(response.json())
    result["request_url"] = response.url
    return result
