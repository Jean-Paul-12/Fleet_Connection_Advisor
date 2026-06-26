from typing import Any

from app.domain.models.weather import LocationData, WeatherForecast
from app.domain.services.weather_service import WeatherService
from app.infrastructure.repositories.city_repository import CityRepository
from app.infrastructure.repositories.forecast_repository import ForecastRepository


class ForecastService:
    def __init__(
        self,
        weather_service: WeatherService,
        city_repository: CityRepository,
        forecast_repository: ForecastRepository,
        weather_api_provider: str = "openweathermap",
    ):
        self._weather_service = weather_service
        self._city_repository = city_repository
        self._forecast_repository = forecast_repository
        self._weather_api_provider = weather_api_provider

    def generate_forecast(self, location: str) -> dict[str, Any]:
        forecast = self._weather_service.get_forecast(location)
        city = self._city_repository.upsert_from_location(
            forecast.location, external_provider=self._weather_api_provider
        )
        saved_forecast = self._forecast_repository.create(city["id"], forecast)
        return {
            "city": city,
            "forecast": self._serialize_forecast(saved_forecast, forecast),
        }

    def get_latest_forecast(self, city_id: str) -> dict[str, Any] | None:
        record = self._forecast_repository.get_latest_by_city(city_id)
        if not record:
            return None
        return record

    def _serialize_forecast(
        self, saved_record: dict[str, Any], forecast: WeatherForecast
    ) -> dict[str, Any]:
        return {
            "id": saved_record.get("id"),
            "city_id": saved_record.get("city_id"),
            "forecast_date": forecast.forecast_date,
            "weather_condition": forecast.weather_condition,
            "rain_probability": forecast.rain_probability,
            "temperature": forecast.temperature,
            "humidity": forecast.humidity,
            "wind_speed": forecast.wind_speed,
            "location": {
                "name": forecast.location.name,
                "region": forecast.location.region,
                "country": forecast.location.country,
                "latitude": forecast.location.latitude,
                "longitude": forecast.location.longitude,
                "timezone": forecast.location.timezone,
            },
        }
