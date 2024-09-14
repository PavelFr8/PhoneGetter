from flask import request, jsonify

from app import db
from app.models import Device
from app.utils import api_token_required

from . import module

# Create device and get him individual API token

# This feature should only be used when creating a device (e.g. in production). In a real product, this
# feature should be removed.
@module.route('/create_device', methods=['POST'])
def create_device():
    name = request.json.get('name')
    ip = request.json.get('ip')
    owner_id = request.json.get('owner_id')

    # Create new device
    device = Device(name=name, ip=ip, owner_id=owner_id)
    db.session.add(device)
    db.session.commit()

    # Generate API token
    token = device.generate_api_token()

    return jsonify({"status": "Device created", "token": token}), 201