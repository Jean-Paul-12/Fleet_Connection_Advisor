import logging
import uuid
from typing import Any

from supabase import Client

from app.domain.models.advisor_result import AdvisorResult
from app.utils.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class AdvisorRepository:
    TABLE = "fleet_advisor_results"

    def __init__(self, client: Client):
        self._client = client

    def create(self, result: AdvisorResult) -> dict[str, Any]:
        payload = {
            "id": str(uuid.uuid4()),
            "city_id": result.city_id,
            "forecast_date": result.forecast.forecast_date,
            "expected_orders": result.fleet.expected_orders,
            "required_couriers": result.fleet.required_couriers,
            "available_couriers": result.fleet.available_couriers,
            "base_cost_per_trip": result.financials.base_cost_per_trip,
            "weather_cost_multiplier": result.financials.weather_cost_multiplier,
            "adjusted_cost_per_trip": result.financials.adjusted_cost_per_trip,
            "normal_operational_cost": result.financials.normal_operational_cost,
            "estimated_operational_cost": result.financials.estimated_operational_cost,
            "incremental_weather_cost": result.financials.incremental_weather_cost,
            "connection_rate": result.financials.connection_rate,
            "target_connection_rate": result.financials.target_connection_rate,
            "connection_gap": result.financials.connection_gap,
            "investment_needed": result.financials.investment_needed,
            "risk_level": result.risk_level,
            "recommendation": result.recommendation,
            "is_simulated": result.fleet.is_simulated,
            "simulation_notes": result.fleet.simulation_notes,
        }
        try:
            response = self._client.table(self.TABLE).insert(payload).execute()
            if not response.data:
                raise DatabaseError("Advisor result creation returned no data.")
            return response.data[0]
        except DatabaseError:
            raise
        except Exception as exc:
            logger.exception("Failed to create advisor result")
            raise DatabaseError("Unable to save advisor result.") from exc

    def get_latest_by_city(self, city_id: str) -> dict[str, Any] | None:
        try:
            response = (
                self._client.table(self.TABLE)
                .select("*")
                .eq("city_id", city_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as exc:
            logger.exception("Failed to get latest advisor result")
            raise DatabaseError("Unable to fetch advisor result.") from exc

    def get_dashboard_by_city(self, city_id: str) -> dict[str, Any]:
        advisor = self.get_latest_by_city(city_id)
        if not advisor:
            raise NotFoundError(
                f"No advisor result found for city id {city_id}."
            )
        return advisor
