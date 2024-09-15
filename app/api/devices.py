import json

from flask import request, jsonify

from app import db
from app.models import Device, User
from app.utils.api_token_required import api_token_required

from . import module

# Create device and get him individual API token

# This route should only be used when creating a device (e.g. in production). In a real product, this
# feature should be removed.
@module.route('/create_device', methods=['POST'])
def create_device():
    name = request.json.get('name')
    ip = request.json.get('ip')

    # Create new device
    device = Device(name=name, ip=ip)
    db.session.add(device)
    db.session.commit()

    # Generate API token
    token = device.generate_api_token()

    return jsonify({"status": "success", "token": token}), 201


@module.route('/register_owner', methods=['POST'])
@api_token_required
def update_data(device):
    """
    Registers a new owner for the device.

    Request JSON body:
        - owner_id (int): The new owner ID to associate with the device.

    return:
        - JSON object with a status of "success" and the name of the device.
        - HTTP 200 status code.
    """
    device.owner_id = request.json.get('owner_id')

    db.session.commit()
    return jsonify({"status": "success", "device": device.name}), 200


@module.route('/update_data', methods=['POST'])
@api_token_required
def update_data(device):
    """
    Updates the device's cell data and tracks changes in user phone history.

    Request JSON body:
        - cells (dict): A JSON-encoded string of the cell data.
        - changed_cell (int): The identifier for the cell that has been changed.

    return:
        - JSON object with a status of "success" and the name of the device.
        - HTTP 200 status code.
    """
    cells = json.loads(request.json.get('cells'))
    changed_cell = request.json.get('changed_cell')
    device.cells = json.dumps(cells)

    user_id = cells[changed_cell][0]
    user: User = db.session.query(User).get(user_id)
    user.phone.update_history(not cells[changed_cell][1])

    db.session.commit()
    return jsonify({"status": "success", "device": device.name}), 200