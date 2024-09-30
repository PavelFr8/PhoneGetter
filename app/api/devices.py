import json
import secrets

from flask import request, jsonify

from app import db
from app.models import Device, User, PhoneHistory, NewClassTokens
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


@module.route('/reset_connection', methods=['GET'])
@api_token_required
def reset_connection(device):
    """
    Remove connection between owner and device. Requires valid API token.

    Request JSON body:
        - owner_id (int): The owner ID to be removed (though not directly used here).

    :param device: The device associated with the provided API token.

    :return: JSON response:
        - status (str): 'success' if the owner is removed successfully.
        - device (str): The name of the device.
        - HTTP status code 200.
    """
    device.owner_id = ''
    device.cells = json.dumps({})
    db.session.commit()

    return jsonify({"status": "success", "device": device.name}), 200


@module.route('/update_data', methods=['PUT'])
@api_token_required
@json_is_valid({"cells": dict[str: list[int, bool]], "changed_cell": int})
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

    device.cells = json.dumps(cells)

    # Extract user ID from the changed cell data and find the user
    user_id = cells[changed_cell][1][0]
    user: User = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if not user.phone:
        phone_history = PhoneHistory(user_id=user.id, history=json.dumps({}))
        db.session.add(phone_history)
        db.session.commit()
        user.phone = phone_history

    # Update user's phone history based on the cell change
    user.phone.update_history(not cells[changed_cell][1])

    db.session.commit()
    return jsonify({"status": "success", "device": device.name}), 200


@module.route('/give_data', methods=['GET'])
@api_token_required
def give_data(device):
    """
    Return to device new data from database.
    Requires valid API token.

    :param device: The device associated with the provided API token.

    :return: JSON response:
        - status (str): 'success' if no errors.
        - device (str): The name of the device.
        - cells (json): The data about cells state.
        - HTTP status code 200.
    """

    return jsonify({"status": "success", "device": device.name, "cells": device.cells}), 200


@module.route('/create_code', methods=['GET'])
@api_token_required
def create_code(device):
    """
    Return to device secret token for registration on the website.
    Requires valid API token.

    :param device: The device associated with the provided API token.

    :return: JSON response:
        - status (str): 'success' if no errors.
        - device (str): The name of the device.
        - code (int): The secret code.
        - HTTP status code 200.
    """
    token = int(secrets.token_hex(3), 16)
    new_link = NewClassTokens(class_id=device.id, token=token)
    db.session.add(new_link)
    db.session.commit()
    return jsonify({"status": "success", "device": device.name, "token": token}), 200