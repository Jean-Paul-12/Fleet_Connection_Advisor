from app.config.settings import Settings
from app.domain.services.simulation_service import SimulationService


def test_simulation_service_generates_simulated_fleet_data():
    settings = Settings(
        flask_env="development",
        flask_app="app.main",
        port=5000,
        supabase_url="",
        supabase_service_role_key="",
        supabase_anon_key="",
        weather_api_provider="weatherapi",
        weather_api_key="",
        weather_api_base_url="https://api.weatherapi.com/v1",
        base_cost_per_trip=1.0,
        rain_cost_multiplier=1.3,
        storm_cost_multiplier=1.5,
        normal_cost_multiplier=1.0,
        target_connection_rate=0.95,
        default_estimated_cost_per_courier_activation=5.0,
        simulation_min_base_orders=8000,
        simulation_max_base_orders=8000,
        simulation_orders_per_courier=4,
        simulation_max_rain_demand_uplift=0.20,
        simulation_max_rain_availability_drop=0.25,
        low_risk_rain_threshold=0.3,
        medium_risk_rain_threshold=0.6,
        high_risk_rain_threshold=0.75,
        cors_allowed_origins=["http://localhost:5173"],
    )

    service = SimulationService(settings)
    fleet = service.generate(rain_probability=0.5)

    assert fleet.is_simulated is True
    assert fleet.expected_orders == 8800
    assert fleet.required_couriers == 2200
    assert fleet.available_couriers == 1925


def test_simulation_service_accepts_manual_override():
    settings = Settings(
        flask_env="development",
        flask_app="app.main",
        port=5000,
        supabase_url="",
        supabase_service_role_key="",
        supabase_anon_key="",
        weather_api_provider="weatherapi",
        weather_api_key="",
        weather_api_base_url="https://api.weatherapi.com/v1",
        base_cost_per_trip=1.0,
        rain_cost_multiplier=1.3,
        storm_cost_multiplier=1.5,
        normal_cost_multiplier=1.0,
        target_connection_rate=0.95,
        default_estimated_cost_per_courier_activation=5.0,
        simulation_min_base_orders=8000,
        simulation_max_base_orders=15000,
        simulation_orders_per_courier=4,
        simulation_max_rain_demand_uplift=0.20,
        simulation_max_rain_availability_drop=0.25,
        low_risk_rain_threshold=0.3,
        medium_risk_rain_threshold=0.6,
        high_risk_rain_threshold=0.75,
        cors_allowed_origins=["http://localhost:5173"],
    )

    service = SimulationService(settings)
    fleet = service.generate(
        rain_probability=0.5,
        manual_data={
            "expected_orders": 12000,
            "required_couriers": 3000,
            "available_couriers": 2500,
        },
    )

    assert fleet.is_simulated is False
    assert fleet.expected_orders == 12000
