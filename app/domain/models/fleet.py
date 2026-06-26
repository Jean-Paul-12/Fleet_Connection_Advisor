from dataclasses import dataclass


@dataclass
class FleetData:
    expected_orders: int
    required_couriers: int
    available_couriers: int
    is_simulated: bool
    simulation_notes: str
