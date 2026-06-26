from app.domain.models.weather import WeatherForecast
from app.infrastructure.clients.weather_api_client import WeatherApiClient


class WeatherService:
    def __init__(self, weather_client: WeatherApiClient):
        self._weather_client = weather_client

    def get_forecast(self, location: str) -> WeatherForecast:
        return self._weather_client.fetch_forecast(location)
