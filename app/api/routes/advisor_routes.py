from flask import Blueprint, current_app, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.domain.models.weather import LocationData, WeatherForecast
from app.schemas.advisor_schema import AdvisorEvaluateSchema
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.response import success_response

advisor_bp = Blueprint("advisor", __name__)


@advisor_bp.post("/advisor/evaluate")
def evaluate_advisor():
    schema = AdvisorEvaluateSchema()
    try:
        payload = schema.load(request.get_json(silent=True) or {})
    except MarshmallowValidationError as exc:
        raise ValidationError("Invalid advisor payload.", details=exc.messages) from exc

    forecast_service = current_app.extensions["forecast_service"]
    fleet_advisor_service = current_app.extensions["fleet_advisor_service"]
    advisor_repository = current_app.extensions["advisor_repository"]

    forecast_result = forecast_service.generate_forecast(payload["location"])
    city = forecast_result["city"]
    forecast_data = forecast_result["forecast"]

    weather_forecast = _build_weather_forecast(forecast_data)
    advisor_result = fleet_advisor_service.evaluate(
        city_id=city["id"],
        forecast=weather_forecast,
        manual_simulation=payload.get("simulation"),
    )

    saved = advisor_repository.create(advisor_result)
    advisor_result.id = saved.get("id")
    advisor_result.created_at = saved.get("created_at")

    response = advisor_result.to_dict()
    response["city"] = city
    return success_response(response, status_code=201)


@advisor_bp.get("/advisor/dashboard")
def get_dashboard():
    city_id = request.args.get("city_id")
    if not city_id:
        raise ValidationError("Query parameter city_id is required.")

    advisor_repository = current_app.extensions["advisor_repository"]
    city_repository = current_app.extensions["city_repository"]
    forecast_repository = current_app.extensions["forecast_repository"]

    advisor = advisor_repository.get_dashboard_by_city(city_id)
    city = city_repository.get_by_id(city_id)
    forecast = forecast_repository.get_latest_by_city(city_id)

    if not forecast:
        raise NotFoundError(f"No forecast found for city id {city_id}.")

    response = _build_dashboard_response(advisor, city, forecast)
    return success_response(response)


def _build_weather_forecast(forecast_data: dict) -> WeatherForecast:
    location_data = forecast_data.get("location", {})
    return WeatherForecast(
        location=LocationData(
            name=location_data.get("name", ""),
            region=location_data.get("region", ""),
            country=location_data.get("country", ""),
            latitude=float(location_data.get("latitude", 0)),
            longitude=float(location_data.get("longitude", 0)),
            timezone=location_data.get("timezone", ""),
        ),
        forecast_date=forecast_data.get("forecast_date", ""),
        weather_condition=forecast_data.get("weather_condition", ""),
        rain_probability=float(forecast_data.get("rain_probability", 0)),
        temperature=float(forecast_data.get("temperature", 0)),
        humidity=float(forecast_data.get("humidity", 0)),
        wind_speed=float(forecast_data.get("wind_speed", 0)),
    )


def _build_dashboard_response(
    advisor: dict, city: dict, forecast: dict
) -> dict:
    return {
        "id": advisor.get("id"),
        "city_id": advisor.get("city_id"),
        "created_at": advisor.get("created_at"),
        "city": city,
        "location": {
            "name": city.get("name"),
            "region": city.get("region"),
            "country": city.get("country"),
            "latitude": city.get("latitude"),
            "longitude": city.get("longitude"),
            "timezone": city.get("timezone"),
        },
        "forecast": {
            "forecast_date": forecast.get("forecast_date"),
            "weather_condition": forecast.get("weather_condition"),
            "rain_probability": forecast.get("rain_probability"),
            "temperature": forecast.get("temperature"),
            "humidity": forecast.get("humidity"),
            "wind_speed": forecast.get("wind_speed"),
        },
        "fleet": {
            "expected_orders": advisor.get("expected_orders"),
            "required_couriers": advisor.get("required_couriers"),
            "available_couriers": advisor.get("available_couriers"),
            "is_simulated": advisor.get("is_simulated"),
            "simulation_notes": advisor.get("simulation_notes"),
        },
        "financials": {
            "base_cost_per_trip": advisor.get("base_cost_per_trip"),
            "weather_cost_multiplier": advisor.get("weather_cost_multiplier"),
            "adjusted_cost_per_trip": advisor.get("adjusted_cost_per_trip"),
            "normal_operational_cost": advisor.get("normal_operational_cost"),
            "estimated_operational_cost": advisor.get("estimated_operational_cost"),
            "incremental_weather_cost": advisor.get("incremental_weather_cost"),
            "connection_rate": advisor.get("connection_rate"),
            "target_connection_rate": advisor.get("target_connection_rate"),
            "connection_gap": advisor.get("connection_gap"),
            "missing_couriers": max(
                0,
                (advisor.get("required_couriers") or 0)
                - (advisor.get("available_couriers") or 0),
            ),
            "investment_needed": advisor.get("investment_needed"),
        },
        "risk_level": advisor.get("risk_level"),
        "recommendation": advisor.get("recommendation"),
    }
