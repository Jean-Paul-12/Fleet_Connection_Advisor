import logging

import requests

from app.config.settings import Settings

logger = logging.getLogger(__name__)

_PROVIDER_HELP = {
    "weatherstack": "https://weatherstack.com/product",
    "openweathermap": "https://openweathermap.org/api",
    "weatherapi": "https://www.weatherapi.com/signup.aspx",
}


def verify_weather_api(settings: Settings) -> None:
    if not settings.weather_api_key:
        logger.warning(
            "WEATHER_API_KEY is not configured. "
            "Forecast and advisor endpoints will fail until it is set."
        )
        return

    provider = settings.weather_api_provider.lower()
    base_url = settings.weather_api_base_url.rstrip("/")

    if provider == "weatherstack":
        url = f"{base_url}/current"
        params = {
            "access_key": settings.weather_api_key,
            "query": "London",
            "units": "m",
        }
    elif provider == "openweathermap" and "/4.0" in base_url:
        url = f"{base_url}/onecall/current"
        params = {
            "appid": settings.weather_api_key,
            "lat": 52.2297,
            "lon": 21.0122,
            "units": "metric",
            "lang": "en",
        }
        fallback_url = "https://api.openweathermap.org/data/2.5/weather"
        fallback_params = {
            "appid": settings.weather_api_key,
            "q": "London",
            "units": "metric",
        }
    elif provider == "openweathermap":
        url = f"{base_url}/forecast"
        params = {
            "appid": settings.weather_api_key,
            "q": "London",
            "units": "metric",
            "cnt": 1,
        }
    elif provider == "weatherapi":
        url = f"{base_url}/forecast.json"
        params = {
            "key": settings.weather_api_key,
            "q": "London",
            "days": 1,
        }
    else:
        logger.error(
            "Unsupported WEATHER_API_PROVIDER=%s. "
            "Use weatherstack, openweathermap or weatherapi.",
            settings.weather_api_provider,
        )
        return

    try:
        response = requests.get(url, params=params, timeout=10)
        if provider == "weatherstack":
            payload = response.json()
            if response.status_code == 200 and payload.get("success") is not False:
                logger.info("Weather API key verified successfully (weatherstack).")
                return
            message = (payload.get("error") or {}).get(
                "info", "Weatherstack rejected the configured key."
            )
        elif response.status_code == 200:
            logger.info("Weather API key verified successfully (%s).", provider)
            return
        else:
            message = "Weather API rejected the configured key."
            try:
                payload = response.json()
                message = payload.get("error", {}).get("message") or payload.get(
                    "message", message
                )
                if isinstance(payload.get("error"), dict):
                    message = payload["error"].get("info") or message
            except Exception:
                pass

        if provider == "openweathermap" and "/4.0" in base_url:
            fallback = requests.get(
                fallback_url, params=fallback_params, timeout=10
            )
            if fallback.status_code == 200:
                logger.info(
                    "Weather API key verified on 2.5 fallback. "
                    "One Call 4.0 is not active for this account yet."
                )
                return

        help_url = _PROVIDER_HELP.get(provider, "")
        logger.error(
            "%s Update WEATHER_API_KEY in backend/.env (%s).",
            message,
            help_url,
        )
    except requests.RequestException:
        logger.warning("Could not verify Weather API key (network error).")
