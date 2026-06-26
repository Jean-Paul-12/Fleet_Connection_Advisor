from flask import Blueprint, current_app, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.schemas.forecast_schema import ForecastGenerateSchema
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.response import success_response

forecast_bp = Blueprint("forecast", __name__)


@forecast_bp.post("/forecast/generate")
def generate_forecast():
    schema = ForecastGenerateSchema()
    try:
        payload = schema.load(request.get_json(silent=True) or {})
    except MarshmallowValidationError as exc:
        raise ValidationError("Invalid forecast payload.", details=exc.messages) from exc

    forecast_service = current_app.extensions["forecast_service"]
    result = forecast_service.generate_forecast(payload["location"])
    return success_response(result, status_code=201)


@forecast_bp.get("/forecast")
def get_forecast():
    city_id = request.args.get("city_id")
    if not city_id:
        raise ValidationError("Query parameter city_id is required.")

    forecast_service = current_app.extensions["forecast_service"]
    forecast = forecast_service.get_latest_forecast(city_id)
    if not forecast:
        raise NotFoundError(f"No forecast found for city id {city_id}.")

    return success_response(forecast)
