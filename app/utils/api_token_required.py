from functools import wraps

from flask import request, jsonify

from app import db
from app.models import Device


# Check API token in request headers
def api_token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Unauthorized"}), 403

        device: Device = db.session.query(Device).filter_by(api_token=token).first()
        if not device:
            return jsonify({"error": "Unauthorized device"}), 403

        return func(device=device, *args, **kwargs)

    return decorated_function
