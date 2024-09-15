import json
from flask import request, jsonify
from app import db
from app.models import Device, User, PhoneHistory
from app.utils.api_token_required import api_token_required
from app.utils.json_is_valid import json_is_valid
from . import module


@module.route('/create_device', methods=['POST'])
@json_is_valid({"name": str, "ip": str})
def create_device():
    """
    Creates a new device and generates an individual API token for it.

    Request JSON body:
        - name (str): The name of the device.
        - ip (str): The IP address of the device.

    :return: JSON response:
        - status (str): 'success' if the device is created successfully.
        - token (str): The generated API token for the device.
        - HTTP status code 201.
    """
    name = request.json['name']
    ip = request.json['ip']

    # Create new device
    device = Device(name=name, ip=ip)

    # Generate API token
    token = device.generate_api_token()

    db.session.add(device)
    db.session.commit()

    return jsonify({"status": "success", "token": token}), 201


@module.route('/register_owner', methods=['POST'])
@api_token_required
@json_is_valid({"owner_id": int})
def register_owner(device):
    """
    Registers a new owner for the device. Requires valid API token.

    Request JSON body:
        - owner_id (int): The user ID to assign as the owner of the device.

    :param device: The device associated with the provided API token.

    :return: JSON response:
        - status (str): 'success' if the owner is registered successfully.
        - device (str): The name of the device.
        - HTTP status code 200.
    """
    owner_id = request.json['owner_id']
    device.owner_id = owner_id

    db.session.commit()
    return jsonify({"status": "success", "device": device.name}), 200


@module.route('/remove_owner', methods=['POST'])
@api_token_required
@json_is_valid({"owner_id": int})
def remove_owner(device):
    """
    Remove owner from device. Requires valid API token.

    Request JSON body:
        - owner_id (int): The owner ID to be removed (though not directly used here).

    :param device: The device associated with the provided API token.

    :return: JSON response:
        - status (str): 'success' if the owner is removed successfully.
        - device (str): The name of the device.
        - HTTP status code 200.
    """
    device.owner_id = None
    db.session.commit()

    return jsonify({"status": "success", "device": device.name}), 200


@module.route('/update_data', methods=['POST'])
@api_token_required
@json_is_valid({"cells": dict, "changed_cell": int})
def update_data(device):
    """
    Updates the device's cell data and tracks changes in the user's phone history.
    Requires valid API token.

    Request JSON body:
        - cells (dict): A dictionary containing the cell data.
        - changed_cell (int): The identifier of the cell that has been updated.

    :param device: The device associated with the provided API token.

    :return: JSON response:
        - status (str): 'success' if the data is updated successfully.
        - device (str): The name of the device.
        - HTTP status code 200, or relevant error codes in case of issues (400 for invalid data, 404 if user not found).
    """
    cells = request.json['cells']
    changed_cell = str(request.json['changed_cell'])

    if changed_cell not in cells:
        return jsonify({"status": "error", "message": "Invalid data for 'changed_cell'"}), 400

    device.cells = cells

    # Extract user ID from the changed cell data and find the user
    user_id = cells[changed_cell][0]
    user: User = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if not user.phone:
        phone_history = PhoneHistory(user_id=user.id)
        db.session.add(phone_history)
        db.session.commit()
        user.phone = phone_history

    # Update user's phone history based on the cell change
    user.phone.update_history(not cells[changed_cell][1])

    db.session.commit()
    return jsonify({"status": "success", "device": device.name}), 200
