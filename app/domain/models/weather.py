from dataclasses import dataclass, field
from typing import Any


@dataclass
class LocationData:
    name: str
    region: str
    country: str
    latitude: float
    longitude: float
    timezone: str


@dataclass
class WeatherForecast:
    location: LocationData
    forecast_date: str
    weather_condition: str
    rain_probability: float
    temperature: float
    humidity: float
    wind_speed: float
    raw_payload: dict[str, Any] = field(default_factory=dict)
