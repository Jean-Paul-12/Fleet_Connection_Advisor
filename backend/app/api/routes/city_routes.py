import uuid

from flask import Blueprint, current_app, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.schemas.city_schema import CityCreateSchema
from app.utils.exceptions import ValidationError
from app.utils.response import success_response

city_bp = Blueprint("cities", __name__)


@city_bp.get("/cities")
def list_cities():
    city_repository = current_app.extensions["city_repository"]
    cities = city_repository.list_recent()
    return success_response(cities)


@city_bp.post("/cities")
def create_city():
    schema = CityCreateSchema()
    try:
        payload = schema.load(request.get_json(silent=True) or {})
    except MarshmallowValidationError as exc:
        raise ValidationError("Invalid city payload.", details=exc.messages) from exc

    payload["id"] = str(uuid.uuid4())
    payload.setdefault("is_active", True)

    city_repository = current_app.extensions["city_repository"]
    city = city_repository.create(payload)
    return success_response(city, status_code=201)
