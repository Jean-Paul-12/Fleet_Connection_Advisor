import logging
import uuid
from typing import Any

from supabase import Client

from app.domain.models.weather import LocationData
from app.utils.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class CityRepository:
    TABLE = "cities"

    def __init__(self, client: Client):
        self._client = client

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        try:
            response = (
                self._client.table(self.TABLE)
                .select("*")
                .eq("is_active", True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as exc:
            logger.exception("Failed to list cities")
            raise DatabaseError("Unable to fetch cities.") from exc

    def get_by_id(self, city_id: str) -> dict[str, Any]:
        try:
            response = (
                self._client.table(self.TABLE)
                .select("*")
                .eq("id", city_id)
                .limit(1)
                .execute()
            )
            if not response.data:
                raise NotFoundError(f"City with id {city_id} was not found.")
            return response.data[0]
        except NotFoundError:
            raise
        except Exception as exc:
            logger.exception("Failed to get city by id")
            raise DatabaseError("Unable to fetch city.") from exc

    def find_by_name_country(
        self, name: str, country: str
    ) -> dict[str, Any] | None:
        try:
            response = (
                self._client.table(self.TABLE)
                .select("*")
                .eq("name", name)
                .eq("country", country)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as exc:
            logger.exception("Failed to find city")
            raise DatabaseError("Unable to find city.") from exc

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.table(self.TABLE).insert(payload).execute()
            if not response.data:
                raise DatabaseError("City creation returned no data.")
            return response.data[0]
        except DatabaseError:
            raise
        except Exception as exc:
            logger.exception("Failed to create city")
            raise DatabaseError("Unable to create city.") from exc

    def upsert_from_location(
        self, location: LocationData, external_provider: str = "openweathermap"
    ) -> dict[str, Any]:
        existing = self.find_by_name_country(location.name, location.country)
        if existing:
            return existing

        payload = {
            "id": str(uuid.uuid4()),
            "name": location.name,
            "region": location.region,
            "country": location.country,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "timezone": location.timezone,
            "external_provider": external_provider,
            "external_location_id": f"{location.latitude},{location.longitude}",
            "is_active": True,
        }
        return self.create(payload)
