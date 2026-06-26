from marshmallow import Schema, fields, validate


class ForecastGenerateSchema(Schema):
    location = fields.Str(required=True, validate=validate.Length(min=1, max=255))


class ForecastResponseSchema(Schema):
    id = fields.Str()
    city_id = fields.Str()
    forecast_date = fields.Str()
    weather_condition = fields.Str()
    rain_probability = fields.Float()
    temperature = fields.Float()
    humidity = fields.Float()
    wind_speed = fields.Float()
    created_at = fields.Str()
