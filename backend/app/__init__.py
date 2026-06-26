from flask import Flask
from flask_cors import CORS

from app.api.error_handlers import register_error_handlers
from app.api.routes.advisor_routes import advisor_bp
from app.api.routes.city_routes import city_bp
from app.api.routes.forecast_routes import forecast_bp
from app.api.routes.health_routes import health_bp
from app.config.logging_config import configure_logging
from app.config.settings import get_settings
from app.config.startup_checks import verify_weather_api
from app.domain.services.fleet_advisor_service import FleetAdvisorService
from app.domain.services.forecast_service import ForecastService
from app.domain.services.weather_service import WeatherService
from app.infrastructure.clients.supabase_client import get_supabase_client
from app.infrastructure.clients.weather_api_client import WeatherApiClient
from app.infrastructure.repositories.advisor_repository import AdvisorRepository
from app.infrastructure.repositories.city_repository import CityRepository
from app.infrastructure.repositories.forecast_repository import ForecastRepository


def create_app() -> Flask:
    configure_logging()
    settings = get_settings()
    verify_weather_api(settings)

    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    CORS(app, resources={r"/api/*": {"origins": settings.cors_allowed_origins}})

    supabase_client = get_supabase_client(settings)
    weather_client = WeatherApiClient(settings)

    city_repository = CityRepository(supabase_client)
    forecast_repository = ForecastRepository(supabase_client)
    advisor_repository = AdvisorRepository(supabase_client)

    weather_service = WeatherService(weather_client)
    forecast_service = ForecastService(
        weather_service,
        city_repository,
        forecast_repository,
        weather_api_provider=settings.weather_api_provider,
    )
    fleet_advisor_service = FleetAdvisorService(settings)

    app.extensions["city_repository"] = city_repository
    app.extensions["forecast_repository"] = forecast_repository
    app.extensions["advisor_repository"] = advisor_repository
    app.extensions["forecast_service"] = forecast_service
    app.extensions["fleet_advisor_service"] = fleet_advisor_service

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(city_bp, url_prefix="/api")
    app.register_blueprint(forecast_bp, url_prefix="/api")
    app.register_blueprint(advisor_bp, url_prefix="/api")

    register_error_handlers(app)
    return app
