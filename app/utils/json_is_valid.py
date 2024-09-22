from functools import wraps
from flask import request, jsonify


# Function to validate the structure of 'cells'
def validate_cells(cells):
    if not isinstance(cells, dict):
        return False
    for key, value in cells.items():
        if not isinstance(key, str):
            return False
        if not isinstance(value, list) or len(value) != 2:
            return False
        if not isinstance(value[0], int) or not isinstance(value[1], bool):
            return False
    return True


# Decorator for checking json data
def json_is_valid(required_fields):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.json
            if not data:
                return jsonify({"status": "error", "message": "No JSON body found"}), 400

            for field, field_type in required_fields.items():
                if field not in data or data[field] is None:
                    return jsonify({"status": "error", "message": f"Missing or null field: {field}"}), 400

                # Custom validation for 'cells'
                if field == 'cells' and not validate_cells(data[field]):
                    return jsonify({"status": "error", "message": "Invalid structure for 'cells'."}), 400

                # Standard type check for non-custom fields
                elif field != 'cells' and not isinstance(data[field], field_type):
                    return jsonify({"status": "error",
                                    "message": f"Invalid type for field: {field}. Expected {field_type.__name__}."}), 400

            return f(*args, **kwargs)

        return wrapper

    return decorator