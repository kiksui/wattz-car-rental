from flask import Blueprint, jsonify, request, abort
from models.car import Car
from models.booking import Booking
from datetime import datetime
from marshmallow import Schema, fields, ValidationError

car_routes = Blueprint('car_routes', __name__)

class DateRangeSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

@car_routes.route('/cars/available', methods=['GET'])
def get_available_cars():
    schema = DateRangeSchema()
    try:
        data = schema.load(request.args)
    except ValidationError as err:
        return jsonify(err.messages), 400

    start_date = data['start_date']
    end_date = data['end_date']

    if start_date > end_date:
        return jsonify({"error": "Start date must be before end date"}), 400

    # ... rest of the function remains the same