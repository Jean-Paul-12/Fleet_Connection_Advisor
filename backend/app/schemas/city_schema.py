from marshmallow import Schema, fields, validate


class CityCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    region = fields.Str(load_default="")
    country = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    timezone = fields.Str(load_default="")
    external_provider = fields.Str(load_default="weatherapi")
    external_location_id = fields.Str(load_default="")


class CityResponseSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    region = fields.Str()
    country = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()
    timezone = fields.Str()
    external_provider = fields.Str()
    external_location_id = fields.Str()
    is_active = fields.Bool()
    created_at = fields.Str()
