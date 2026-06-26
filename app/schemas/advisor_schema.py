from marshmallow import Schema, fields, validate


class SimulationOverrideSchema(Schema):
    expected_orders = fields.Int(required=True, validate=validate.Range(min=1))
    required_couriers = fields.Int(required=True, validate=validate.Range(min=1))
    available_couriers = fields.Int(required=True, validate=validate.Range(min=0))


class AdvisorEvaluateSchema(Schema):
    location = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    simulation = fields.Nested(SimulationOverrideSchema, required=False)
