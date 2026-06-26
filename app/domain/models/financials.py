from dataclasses import dataclass


@dataclass
class FinancialResult:
    base_cost_per_trip: float
    weather_cost_multiplier: float
    adjusted_cost_per_trip: float
    normal_operational_cost: float
    estimated_operational_cost: float
    incremental_weather_cost: float
    connection_rate: float
    target_connection_rate: float
    connection_gap: float
    missing_couriers: int
    investment_needed: float
