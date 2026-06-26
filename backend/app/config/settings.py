import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    flask_env: str
    flask_app: str
    port: int

    supabase_url: str
    supabase_service_role_key: str
    supabase_anon_key: str

    weather_api_provider: str
    weather_api_key: str
    weather_api_base_url: str

    base_cost_per_trip: float
    rain_cost_multiplier: float
    storm_cost_multiplier: float
    normal_cost_multiplier: float

    target_connection_rate: float
    default_estimated_cost_per_courier_activation: float

    simulation_min_base_orders: int
    simulation_max_base_orders: int
    simulation_orders_per_courier: int
    simulation_max_rain_demand_uplift: float
    simulation_max_rain_availability_drop: float

    low_risk_rain_threshold: float
    medium_risk_rain_threshold: float
    high_risk_rain_threshold: float

    cors_allowed_origins: list[str]


@lru_cache
def get_settings() -> Settings:
    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    return Settings(
        flask_env=os.getenv("FLASK_ENV", "development"),
        flask_app=os.getenv("FLASK_APP", "app.main"),
        port=int(os.getenv("PORT", "5000")),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        weather_api_provider=os.getenv("WEATHER_API_PROVIDER", "weatherstack"),
        weather_api_key=os.getenv("WEATHER_API_KEY", ""),
        weather_api_base_url=os.getenv(
            "WEATHER_API_BASE_URL",
            os.getenv("WEATHER_BASE_URL", "http://api.weatherstack.com"),
        ),
        base_cost_per_trip=float(os.getenv("BASE_COST_PER_TRIP", "1.0")),
        rain_cost_multiplier=float(os.getenv("RAIN_COST_MULTIPLIER", "1.3")),
        storm_cost_multiplier=float(os.getenv("STORM_COST_MULTIPLIER", "1.5")),
        normal_cost_multiplier=float(os.getenv("NORMAL_COST_MULTIPLIER", "1.0")),
        target_connection_rate=float(os.getenv("TARGET_CONNECTION_RATE", "0.95")),
        default_estimated_cost_per_courier_activation=float(
            os.getenv("DEFAULT_ESTIMATED_COST_PER_COURIER_ACTIVATION", "5.0")
        ),
        simulation_min_base_orders=int(os.getenv("SIMULATION_MIN_BASE_ORDERS", "8000")),
        simulation_max_base_orders=int(os.getenv("SIMULATION_MAX_BASE_ORDERS", "15000")),
        simulation_orders_per_courier=int(os.getenv("SIMULATION_ORDERS_PER_COURIER", "4")),
        simulation_max_rain_demand_uplift=float(
            os.getenv("SIMULATION_MAX_RAIN_DEMAND_UPLIFT", "0.20")
        ),
        simulation_max_rain_availability_drop=float(
            os.getenv("SIMULATION_MAX_RAIN_AVAILABILITY_DROP", "0.25")
        ),
        low_risk_rain_threshold=float(os.getenv("LOW_RISK_RAIN_THRESHOLD", "0.3")),
        medium_risk_rain_threshold=float(os.getenv("MEDIUM_RISK_RAIN_THRESHOLD", "0.6")),
        high_risk_rain_threshold=float(os.getenv("HIGH_RISK_RAIN_THRESHOLD", "0.75")),
        cors_allowed_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    )
