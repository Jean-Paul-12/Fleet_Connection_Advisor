from dataclasses import dataclass, field
from typing import Any

from app.domain.models.financials import FinancialResult
from app.domain.models.fleet import FleetData
from app.domain.models.weather import LocationData, WeatherForecast


@dataclass
class AdvisorResult:
    city_id: str
    location: LocationData
    forecast: WeatherForecast
    fleet: FleetData
    financials: FinancialResult
    risk_level: str
    recommendation: str
    id: str | None = None
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "city_id": self.city_id,
            "created_at": self.created_at,
            "location": {
                "name": self.location.name,
                "region": self.location.region,
                "country": self.location.country,
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "timezone": self.location.timezone,
            },
            "forecast": {
                "forecast_date": self.forecast.forecast_date,
                "weather_condition": self.forecast.weather_condition,
                "rain_probability": self.forecast.rain_probability,
                "temperature": self.forecast.temperature,
                "humidity": self.forecast.humidity,
                "wind_speed": self.forecast.wind_speed,
            },
            "fleet": {
                "expected_orders": self.fleet.expected_orders,
                "required_couriers": self.fleet.required_couriers,
                "available_couriers": self.fleet.available_couriers,
                "is_simulated": self.fleet.is_simulated,
                "simulation_notes": self.fleet.simulation_notes,
            },
            "financials": {
                "base_cost_per_trip": self.financials.base_cost_per_trip,
                "weather_cost_multiplier": self.financials.weather_cost_multiplier,
                "adjusted_cost_per_trip": self.financials.adjusted_cost_per_trip,
                "normal_operational_cost": self.financials.normal_operational_cost,
                "estimated_operational_cost": self.financials.estimated_operational_cost,
                "incremental_weather_cost": self.financials.incremental_weather_cost,
                "connection_rate": self.financials.connection_rate,
                "target_connection_rate": self.financials.target_connection_rate,
                "connection_gap": self.financials.connection_gap,
                "missing_couriers": self.financials.missing_couriers,
                "investment_needed": self.financials.investment_needed,
            },
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
        }
