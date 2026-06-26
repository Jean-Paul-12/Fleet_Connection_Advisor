from app.config.settings import Settings
from app.domain.models.financials import FinancialResult
from app.domain.models.fleet import FleetData
from app.domain.models.weather import WeatherForecast


class FinancialService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def calculate(self, forecast: WeatherForecast, fleet: FleetData) -> FinancialResult:
        base_cost = self._settings.base_cost_per_trip
        weather_multiplier = self._resolve_weather_multiplier(forecast)
        adjusted_cost = base_cost * weather_multiplier

        normal_operational_cost = fleet.expected_orders * base_cost
        estimated_operational_cost = fleet.expected_orders * adjusted_cost
        incremental_weather_cost = estimated_operational_cost - normal_operational_cost

        connection_rate = (
            fleet.available_couriers / fleet.required_couriers
            if fleet.required_couriers > 0
            else 0.0
        )
        target_rate = self._settings.target_connection_rate
        connection_gap = max(0.0, target_rate - connection_rate)
        missing_couriers = max(0, fleet.required_couriers - fleet.available_couriers)
        investment_needed = incremental_weather_cost + (
            missing_couriers * self._settings.default_estimated_cost_per_courier_activation
        )

        return FinancialResult(
            base_cost_per_trip=round(base_cost, 4),
            weather_cost_multiplier=round(weather_multiplier, 4),
            adjusted_cost_per_trip=round(adjusted_cost, 4),
            normal_operational_cost=round(normal_operational_cost, 2),
            estimated_operational_cost=round(estimated_operational_cost, 2),
            incremental_weather_cost=round(incremental_weather_cost, 2),
            connection_rate=round(connection_rate, 4),
            target_connection_rate=round(target_rate, 4),
            connection_gap=round(connection_gap, 4),
            missing_couriers=missing_couriers,
            investment_needed=round(investment_needed, 2),
        )

    def _resolve_weather_multiplier(self, forecast: WeatherForecast) -> float:
        condition = forecast.weather_condition.lower()
        rain_probability = forecast.rain_probability

        if (
            "thunder" in condition
            or "storm" in condition
            or rain_probability >= self._settings.high_risk_rain_threshold
        ):
            return self._settings.storm_cost_multiplier

        if rain_probability >= self._settings.medium_risk_rain_threshold:
            return self._settings.rain_cost_multiplier

        return self._settings.normal_cost_multiplier
