import copy
from datetime import datetime
import json
import requests

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from flask_babel import lazy_gettext as _l

from app.utils.generate_invite_link import generate_invite_link
from . import module, forms
from app import db, logger
from app.models import InviteLink, User, Device, PhoneHistory, NewClassTokens


# Create "Your classes" page
@module.route('/')
@login_required
def classes():
    try:
        study_classes = current_user.get_classes()
        devices = Device.query.all()
        if study_classes:
            for study_cls in study_classes:
                study_cls.student = False
        user_devices = []
        if devices:
            for device in devices:
                device = copy.deepcopy(device)
                try:
                    device.cells = json.loads(device.cells)
                except:
                    pass
                for value in device.cells.values():
                    if value[0] == current_user.id:
                        device.student = True
                        state_translations = {"in": _l("in"), "outside": _l("outside")}
                        device.state = state_translations['in'] if value[1] else state_translations['outside']
                        user_devices.append(device)
                        break
        if study_classes:
            study_classes.extend(user_devices)
        else:
            study_classes = user_devices
        logger.debug(f"Returning classes data for user {current_user.id}")
    except Exception as e:
        logger.error(f"Error occurred while fetching classes for user {current_user.id}: {e}")
        study_classes = None
    return render_template('classes/classes.html', title=_l('Your classes'), study_classes=study_classes, form=forms.SecretCodeForm())


# Create "Class <Name>" page
@module.route('/class/<int:id>', methods=['GET', 'POST'])
@login_required
def study_class(id):
    form = forms.InviteForm()
    phone_class = None
    for _class in current_user.get_classes():
        if _class.id == id:
            phone_class = _class
            break

    students_with_phones = []
    students_without_phones = []

    for cell, info in phone_class.cells.items():
        student = db.session.query(User).filter(User.id == info[0]).first()
        student_name = f"{student.name} {student.surname}"
        student_info = {
            'id': info[0],
            'name': student_name,
            'phone_status': info[1],
            'cell_id': cell
        }
        if info[1]:
            students_with_phones.append(student_info)
        else:
            students_without_phones.append(student_info)

    students_with_phones = sorted(students_with_phones, key=lambda x: x['name'])
    students_without_phones = sorted(students_without_phones, key=lambda x: x['name'])

    return render_template('classes/class.html',
                           title=phone_class.name,
                           class_id=phone_class.id,
                           students_with_phones=students_with_phones,
                           students_without_phones=students_without_phones,
                           form=form, form2=forms.ChangeClassNameForm())


# Create new class
@module.route('/class/new', methods=['POST'])
@login_required
def add_by_code():
    form = forms.SecretCodeForm()
    if form.validate_on_submit():
        secret_code = form.secret_code.data
        connection: NewClassTokens = NewClassTokens.query.filter_by(token=secret_code).first()

        if not connection:
            return jsonify({'status': 'error', 'message': _l('Invalid secret code. Please try again.')}), 400

        if connection.expires_at > datetime.utcnow():
            device: Device = db.session.query(Device).get(connection.class_id)
            if device.owner_id:
                return jsonify({"status": "error", "message": _l("Device already has owner")}), 404

            device.owner_id = current_user.id
            db.session.commit()
            logger.info(f"User {current_user.id} successfully added device {device.id} to their classes")
            return jsonify({'status': 'success', 'message': _l('Class added successfully!')}), 200
        else:
            logger.debug(f"Secret code expired for user {current_user.id}: {secret_code}")
            connections: list[NewClassTokens] = NewClassTokens.query.where(NewClassTokens.expires_at <= datetime.utcnow()).all()
            for conn in connections:
                db.session.delete(conn)
            db.session.commit()
            return jsonify({'status': 'error', 'message': _l('Too old secret code')}), 404
    else:
        logger.error(f"Form validation failed for user {current_user.id}")
        return jsonify({'status': 'error', 'message': _l('Form validation failed.')}), 400


# Create unique link to invite user to class
@module.route('class/generate_invite/<int:class_id>', methods=['POST'])
@login_required
def generate_invite(class_id):
    invite_link = generate_invite_link(class_id)
    return jsonify({'link': invite_link})


# Add user to class by link
@module.route('/class/<int:class_id>/invite/<string:token>', methods=['GET'])
@login_required
def invite_student(class_id, token):
    invite_link = InviteLink.query.filter_by(class_id=class_id, token=token).first()
    if invite_link:
        if invite_link.expires_at > datetime.utcnow():
            user: User = current_user
            device: Device = db.session.query(Device).get(class_id)

            cells = json.loads(device.cells)

            if len(cells) >= 25:
                logger.debug(f"User {user.id} tried to join device {device.id} but cell limit reached")
                return render_template('classes/users_limit.html'), 403
            if not user.phone:
                phone_history = PhoneHistory(user_id=user.id, history=json.dumps({}))
                db.session.add(phone_history)
                db.session.commit()
                user.phone = phone_history

            for cell in cells.values():
                if cell[0] == user.id:
                    logger.info(f"User {user.id} already added to device {device.id}")
                    return render_template('classes/added.html', name=device.name), 200
            try:
                available_cells = set(list(range(1, 31))) - set([int(cell) for cell in cells.keys()])
                cells[str(min(available_cells))] = [user.id, False]
            except:
                cells["1"] = [user.id, False]

            device.cells = json.dumps(cells)

            db.session.commit()
            return render_template('classes/added.html', name=device.name), 200
        else:
            expires_links = InviteLink.query.where(InviteLink.invite_link.expires_at <= datetime.utcnow()).all()
            for elem in expires_links:
                db.session.delete(elem)
            db.session.commit()
            logger.debug(f"Invite link expired for class {class_id} and token {token}")
            return render_template('errors/bad_link.html'), 403
    else:
        logger.debug(f"Invalid invite link for class {class_id} and token {token}")
        return render_template('errors/bad_link.html'), 403


# Remove user from class
@module.route('/class/<int:class_id>/remove/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user(class_id, user_id):
    device: Device = db.session.query(Device).get(class_id)

    if device.owner_id != current_user.id:
        logger.debug(f"User {current_user.id} attempted to remove user {user_id} from device {device.id} without permission")
        return jsonify({'status': 'error', 'message': _l('Permission denied')}), 403

    cells = json.loads(device.cells)

    for cell, cell_data in cells.items():
        if cell_data[0] == user_id:
            logger.info(f"Removing user {user_id} from device {device.id}")
            del cells[cell]
            break

    device.cells = json.dumps(cells)

    db.session.commit()

    return jsonify({"status": "success", "device": device.name}), 200


# Change class name
@module.route('/class/<int:class_id>/change_name', methods=['PUT'])
@login_required
def change_class_name(class_id):
    device: Device = db.session.query(Device).get(class_id)

    if device.owner_id != current_user.id:
        logger.debug(f"User {current_user.id} attempted to change name of device {device.id} without permission")
        return jsonify({'status': 'error', 'message': _l('Permission denied')}), 403

    new_name = request.json.get('name', '').strip()
    if not new_name:
        logger.debug(f"User {current_user.id} tried to set empty name for device {device.id}")
        return jsonify({'status': 'error', 'message': _l('Class name cannot be empty')}), 400

    device.name = new_name

    db.session.commit()
    logger.info(f"User {current_user.id} successfully changed the name of device {device.id} to '{new_name}'")

    return jsonify({"status": "success", "device": device.name}), 200


# Return phone to user in class
@module.route('/class/<int:class_id>/return_phone/<int:user_id>', methods=['GET'])
@login_required
def return_phone(class_id, user_id):
    device: Device = db.session.query(Device).get(class_id)

    if device.owner_id != current_user.id:
        logger.debug(f"User {current_user.id} attempted to remove user {user_id} from device {device.id} without permission")
        return jsonify({'status': 'error', 'message': _l('Permission denied')}), 403

    cells = json.loads(device.cells)

    user_cell = -1
    for cell, cell_data in cells.items():
        if cell_data[0] == user_id:
            user_cell = int(cell)
            break
    if user_cell == -1:
        return jsonify({'status': 'error', 'message': _l('Unknown user')}), 403

    r = requests.post("https://phonegetter-mqtt.onrender.com/send_command",
                      json={
                            "device_api_token": device.api_token,
                            "cell_id": user_cell,
                           })
    if r.json()['status'] == 'success':
        cells[user_cell] = [user_id, False]
        device.cells = json.dumps(cells)
        db.session.commit()
        logger.info(f"User {current_user.id} successfully return phone to User {user_id}")
        return jsonify({"status": "success", "device": device.name}), 200
    else:
        logger.error(f"User {current_user.id} failed returning phone to User {user_id}")
        return jsonify({'status': 'error', 'message': _l('')}), 403
