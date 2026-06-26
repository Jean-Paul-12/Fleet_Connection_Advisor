import logging
import math
import random
from typing import Any

from app.config.settings import Settings
from app.domain.models.fleet import FleetData
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SimulationService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def generate(self, rain_probability: float, manual_data: dict[str, Any] | None = None) -> FleetData:
        if manual_data:
            return self._from_manual(manual_data)

        base_expected_orders = random.randint(
            self._settings.simulation_min_base_orders,
            self._settings.simulation_max_base_orders,
        )
        rain_demand_factor = 1 + (
            rain_probability * self._settings.simulation_max_rain_demand_uplift
        )
        expected_orders = round(base_expected_orders * rain_demand_factor)

        required_couriers = math.ceil(
            expected_orders / self._settings.simulation_orders_per_courier
        )
        availability_factor = 1 - (
            rain_probability * self._settings.simulation_max_rain_availability_drop
        )
        available_couriers = math.floor(required_couriers * availability_factor)

        return FleetData(
            expected_orders=expected_orders,
            required_couriers=required_couriers,
            available_couriers=available_couriers,
            is_simulated=True,
            simulation_notes=(
                "Operational demand and courier availability were simulated because "
                "no real internal demand or fleet source was provided."
            ),
        )

    def _from_manual(self, manual_data: dict[str, Any]) -> FleetData:
        required_fields = ("expected_orders", "required_couriers", "available_couriers")
        missing = [field for field in required_fields if field not in manual_data]
        if missing:
            raise ValidationError(
                f"Missing simulation fields: {', '.join(missing)}",
                details={"missing_fields": missing},
            )

        return FleetData(
            expected_orders=int(manual_data["expected_orders"]),
            required_couriers=int(manual_data["required_couriers"]),
            available_couriers=int(manual_data["available_couriers"]),
            is_simulated=False,
            simulation_notes=(
                "Operational demand and courier availability were provided manually "
                "in the request."
            ),
        )
