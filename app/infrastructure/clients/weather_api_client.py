import logging
from datetime import datetime, timezone
from typing import Any

import requests

from app.config.settings import Settings
from app.domain.models.weather import LocationData, WeatherForecast
from app.utils.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

OPENWEATHER_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"


class WeatherApiClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def fetch_forecast(self, location_query: str) -> WeatherForecast:
        if not location_query or not location_query.strip():
            raise ValidationError("Location query is required.")

        if not self._settings.weather_api_key:
            raise ExternalServiceError("Weather API key is not configured.")

        provider = self._settings.weather_api_provider.lower()
        if provider == "weatherstack":
            return self._fetch_weatherstack(location_query.strip())
        if provider == "openweathermap":
            return self._fetch_openweathermap(location_query.strip())
        if provider == "weatherapi":
            return self._fetch_weatherapi(location_query.strip())

        raise ExternalServiceError(
            f"Unsupported weather provider: {self._settings.weather_api_provider}"
        )

    def _fetch_weatherstack(self, location_query: str) -> WeatherForecast:
        base_url = self._settings.weather_api_base_url.rstrip("/")
        url = f"{base_url}/current"
        params = {
            "access_key": self._settings.weather_api_key,
            "query": location_query,
            "units": "m",
        }

        payload = self._request_weatherstack(url, params)
        return self._normalize_weatherstack_response(payload)

    def _request_weatherstack(
        self, url: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            response = requests.get(url, params=params, timeout=15)
            payload = response.json()
        except requests.RequestException as exc:
            logger.exception("Weatherstack request error")
            raise ExternalServiceError("Unable to reach Weatherstack.") from exc
        except ValueError as exc:
            logger.exception("Weatherstack returned invalid JSON")
            raise ExternalServiceError("Invalid Weatherstack response format.") from exc

        if payload.get("success") is False:
            error = payload.get("error") or {}
            message = error.get("info") or "Weatherstack request failed."
            raise ExternalServiceError(message)

        if not response.ok:
            raise ExternalServiceError(
                f"Weatherstack request failed with status {response.status_code}."
            )

        return payload

    def _fetch_weatherapi(self, location_query: str) -> WeatherForecast:
        url = f"{self._settings.weather_api_base_url.rstrip('/')}/forecast.json"
        params = {
            "key": self._settings.weather_api_key,
            "q": location_query,
            "days": 1,
            "aqi": "no",
            "alerts": "no",
        }

        payload = self._request_json(url, params, provider_label="WeatherAPI")
        return self._normalize_weatherapi_response(payload)

    def _fetch_openweathermap(self, location_query: str) -> WeatherForecast:
        base_url = self._settings.weather_api_base_url.rstrip("/")
        if "/4.0" in base_url:
            try:
                return self._fetch_openweathermap_v4(location_query, base_url)
            except ExternalServiceError as exc:
                message = str(exc).lower()
                if self._should_fallback_to_v25(message):
                    logger.warning(
                        "One Call 4.0 unavailable (%s). Falling back to API 2.5 forecast.",
                        exc,
                    )
                    return self._fetch_openweathermap_v25(
                        location_query, "https://api.openweathermap.org/data/2.5"
                    )
                raise
        return self._fetch_openweathermap_v25(location_query, base_url)

    @staticmethod
    def _should_fallback_to_v25(message: str) -> bool:
        return any(
            token in message
            for token in (
                "subscription",
                "one call",
                "invalid api key",
                "unauthorized",
            )
        )

    def _fetch_openweathermap_v25(
        self, location_query: str, base_url: str
    ) -> WeatherForecast:
        url = f"{base_url}/forecast"
        params = {
            "appid": self._settings.weather_api_key,
            "q": location_query,
            "units": "metric",
            "cnt": 8,
        }

        payload = self._request_json(url, params, provider_label="OpenWeatherMap")
        return self._normalize_openweathermap_v25_response(payload)

    def _fetch_openweathermap_v4(
        self, location_query: str, base_url: str
    ) -> WeatherForecast:
        geo = self._geocode_openweathermap(location_query)
        lat = float(geo["lat"])
        lon = float(geo["lon"])

        common_params = {
            "appid": self._settings.weather_api_key,
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "lang": "en",
        }

        current_payload = self._request_json(
            f"{base_url}/onecall/current",
            common_params,
            provider_label="OpenWeatherMap One Call 4.0",
        )

        daily_pop: float | None = None
        try:
            daily_payload = self._request_json(
                f"{base_url}/onecall/timeline/1day",
                common_params,
                provider_label="OpenWeatherMap One Call 4.0",
            )
            daily_items = daily_payload.get("data") or []
            if daily_items:
                daily_pop = float(daily_items[0].get("pop", 0))
        except ExternalServiceError:
            logger.warning("Daily timeline unavailable; estimating rain probability.")

        return self._normalize_openweathermap_v4_response(
            current_payload, geo, daily_pop
        )

    def _geocode_openweathermap(self, location_query: str) -> dict[str, Any]:
        payload = self._request_json(
            OPENWEATHER_GEO_URL,
            {
                "q": location_query,
                "limit": 1,
                "appid": self._settings.weather_api_key,
            },
            provider_label="OpenWeatherMap Geocoding",
        )
        if not payload:
            raise ExternalServiceError(
                f"No location found for '{location_query}'."
            )
        return payload[0]

    def _request_json(
        self, url: str, params: dict[str, Any], provider_label: str
    ) -> dict[str, Any]:
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            return data
        except requests.HTTPError as exc:
            logger.exception("%s HTTP error", provider_label)
            message = f"{provider_label} request failed."
            try:
                error_payload = exc.response.json()
                if "error" in error_payload:
                    message = error_payload["error"].get("message", message)
                elif "message" in error_payload:
                    message = error_payload["message"]
            except Exception:
                pass
            raise ExternalServiceError(message) from exc
        except requests.RequestException as exc:
            logger.exception("%s request error", provider_label)
            raise ExternalServiceError(f"Unable to reach {provider_label}.") from exc

    def _normalize_weatherapi_response(self, payload: dict[str, Any]) -> WeatherForecast:
        try:
            location = payload["location"]
            day = payload["forecast"]["forecastday"][0]
            day_info = day["day"]
            condition = day_info["condition"]["text"]
            rain_probability = float(day_info.get("daily_chance_of_rain", 0)) / 100.0

            location_data = LocationData(
                name=location.get("name", ""),
                region=location.get("region", ""),
                country=location.get("country", ""),
                latitude=float(location.get("lat", 0)),
                longitude=float(location.get("lon", 0)),
                timezone=location.get("tz_id", ""),
            )

            return WeatherForecast(
                location=location_data,
                forecast_date=day.get("date", ""),
                weather_condition=condition,
                rain_probability=rain_probability,
                temperature=float(day_info.get("avgtemp_c", 0)),
                humidity=float(day_info.get("avghumidity", 0)),
                wind_speed=float(day_info.get("maxwind_kph", 0)),
                raw_payload=payload,
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.exception("Failed to normalize WeatherAPI response")
            raise ExternalServiceError("Invalid Weather API response format.") from exc

    def _normalize_openweathermap_v25_response(
        self, payload: dict[str, Any]
    ) -> WeatherForecast:
        try:
            city = payload["city"]
            forecast_items = payload["list"]
            if not forecast_items:
                raise KeyError("list")

            first_item = forecast_items[0]
            forecast_date = datetime.fromtimestamp(
                first_item["dt"], tz=timezone.utc
            ).strftime("%Y-%m-%d")

            rain_probability = max(float(item.get("pop", 0)) for item in forecast_items)
            temperature = sum(item["main"]["temp"] for item in forecast_items) / len(
                forecast_items
            )
            humidity = sum(item["main"]["humidity"] for item in forecast_items) / len(
                forecast_items
            )
            wind_speed = max(float(item["wind"]["speed"]) for item in forecast_items) * 3.6

            wettest_item = max(
                forecast_items, key=lambda item: float(item.get("pop", 0))
            )
            weather_condition = wettest_item["weather"][0]["description"].title()

            location_data = LocationData(
                name=city.get("name", ""),
                region="",
                country=city.get("country", ""),
                latitude=float(city["coord"]["lat"]),
                longitude=float(city["coord"]["lon"]),
                timezone=str(city.get("timezone", "")),
            )

            return WeatherForecast(
                location=location_data,
                forecast_date=forecast_date,
                weather_condition=weather_condition,
                rain_probability=rain_probability,
                temperature=round(temperature, 1),
                humidity=round(humidity, 1),
                wind_speed=round(wind_speed, 1),
                raw_payload=payload,
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.exception("Failed to normalize OpenWeatherMap 2.5 response")
            raise ExternalServiceError("Invalid OpenWeatherMap response format.") from exc

    def _normalize_openweathermap_v4_response(
        self,
        payload: dict[str, Any],
        geo: dict[str, Any],
        daily_pop: float | None,
    ) -> WeatherForecast:
        try:
            current_items = payload.get("data") or []
            if not current_items:
                raise KeyError("data")

            current = current_items[0]
            forecast_date = datetime.fromtimestamp(
                current["dt"], tz=timezone.utc
            ).strftime("%Y-%m-%d")
            weather = current["weather"][0]
            weather_condition = weather.get("description", weather.get("main", "")).title()

            rain_probability = (
                daily_pop
                if daily_pop is not None
                else self._estimate_rain_probability(current)
            )

            location_data = LocationData(
                name=geo.get("name", ""),
                region=geo.get("state", "") or "",
                country=geo.get("country", ""),
                latitude=float(payload.get("lat", geo.get("lat", 0))),
                longitude=float(payload.get("lon", geo.get("lon", 0))),
                timezone=str(payload.get("timezone", "")),
            )

            return WeatherForecast(
                location=location_data,
                forecast_date=forecast_date,
                weather_condition=weather_condition,
                rain_probability=round(rain_probability, 2),
                temperature=round(float(current["temp"]), 1),
                humidity=round(float(current["humidity"]), 1),
                wind_speed=round(float(current["wind_speed"]) * 3.6, 1),
                raw_payload={"current": payload, "geo": geo},
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.exception("Failed to normalize OpenWeatherMap 4.0 response")
            raise ExternalServiceError("Invalid OpenWeatherMap response format.") from exc

    def _normalize_weatherstack_response(
        self, payload: dict[str, Any]
    ) -> WeatherForecast:
        try:
            location = payload["location"]
            current = payload["current"]
            descriptions = current.get("weather_descriptions") or []
            weather_condition = descriptions[0] if descriptions else "Unknown"

            localtime = str(location.get("localtime", ""))
            forecast_date = localtime.split(" ", 1)[0] if localtime else datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d")

            location_data = LocationData(
                name=location.get("name", ""),
                region=location.get("region", "") or "",
                country=location.get("country", ""),
                latitude=float(location.get("lat", 0)),
                longitude=float(location.get("lon", 0)),
                timezone=location.get("timezone_id", "") or "",
            )

            return WeatherForecast(
                location=location_data,
                forecast_date=forecast_date,
                weather_condition=weather_condition,
                rain_probability=self._estimate_weatherstack_rain_probability(current),
                temperature=round(float(current.get("temperature", 0)), 1),
                humidity=round(float(current.get("humidity", 0)), 1),
                wind_speed=round(float(current.get("wind_speed", 0)), 1),
                raw_payload=payload,
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.exception("Failed to normalize Weatherstack response")
            raise ExternalServiceError("Invalid Weatherstack response format.") from exc

    @staticmethod
    def _estimate_weatherstack_rain_probability(current: dict[str, Any]) -> float:
        precip = float(current.get("precip", 0) or 0)
        if precip > 0:
            return min(1.0, 0.45 + precip / 15.0)

        description = " ".join(current.get("weather_descriptions") or []).lower()
        if any(
            token in description
            for token in ("rain", "shower", "drizzle", "thunder", "storm")
        ):
            return 0.72

        weather_code = int(current.get("weather_code", 0) or 0)
        if 176 <= weather_code <= 299:
            return 0.65

        cloudcover = float(current.get("cloudcover", 0) or 0)
        if cloudcover > 70:
            return 0.35
        return 0.12

    @staticmethod
    def _estimate_rain_probability(current: dict[str, Any]) -> float:
        rain_mm = float(current.get("rain", {}).get("1h", 0) or 0)
        if rain_mm > 0:
            return min(1.0, 0.5 + rain_mm / 20.0)

        weather_main = (current.get("weather") or [{}])[0].get("main", "").lower()
        if weather_main in {"rain", "drizzle", "thunderstorm"}:
            return 0.75
        if weather_main == "clouds":
            return 0.35
        return 0.1
