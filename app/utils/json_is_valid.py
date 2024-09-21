from functools import wraps
from flask import request, jsonify


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
                if not isinstance(data[field], field_type):
                    return jsonify({"status": "error",
                                    "message": f"Invalid type for field: {field}. Expected {field_type.__name__}."}), 400

            return f(*args, **kwargs)

        return wrapper

    return decorator