import logging
import uuid
from typing import Any

from supabase import Client

from app.domain.models.weather import WeatherForecast
from app.utils.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class ForecastRepository:
    TABLE = "weather_forecasts"

    def __init__(self, client: Client):
        self._client = client

    def create(self, city_id: str, forecast: WeatherForecast) -> dict[str, Any]:
        payload = {
            "id": str(uuid.uuid4()),
            "city_id": city_id,
            "forecast_date": forecast.forecast_date,
            "weather_condition": forecast.weather_condition,
            "rain_probability": forecast.rain_probability,
            "temperature": forecast.temperature,
            "humidity": forecast.humidity,
            "wind_speed": forecast.wind_speed,
            "raw_payload": forecast.raw_payload,
        }
        try:
            response = self._client.table(self.TABLE).insert(payload).execute()
            if not response.data:
                raise DatabaseError("Forecast creation returned no data.")
            return response.data[0]
        except DatabaseError:
            raise
        except Exception as exc:
            logger.exception("Failed to create forecast")
            raise DatabaseError("Unable to save forecast.") from exc

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
            logger.exception("Failed to get latest forecast")
            raise DatabaseError("Unable to fetch forecast.") from exc

    def get_by_id(self, forecast_id: str) -> dict[str, Any]:
        try:
            response = (
                self._client.table(self.TABLE)
                .select("*")
                .eq("id", forecast_id)
                .limit(1)
                .execute()
            )
            if not response.data:
                raise NotFoundError(f"Forecast with id {forecast_id} was not found.")
            return response.data[0]
        except NotFoundError:
            raise
        except Exception as exc:
            logger.exception("Failed to get forecast by id")
            raise DatabaseError("Unable to fetch forecast.") from exc
