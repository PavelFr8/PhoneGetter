from datetime import datetime
import json

from flask import render_template, jsonify
from flask_login import login_required, current_user
from flask_babel import lazy_gettext as _l

from app.utils.generate_invite_link import generate_invite_link
from . import module, forms
from app import db
from app.models import InviteLink, User, Device, PhoneHistory, NewClassTokens


# Create "Your classes" page
@module.route('/')
@login_required
def classes():
    try:
        study_classes = current_user.get_classes()
    except Exception as e:
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
                           form=form)


# Create new class
@module.route('/class/new', methods=['POST'])
@login_required
def add_by_code():
    form = forms.SecretCodeForm()
    if form.validate_on_submit():
        secret_code = form.secret_code.data
        connection: NewClassTokens = NewClassTokens.query.filter_by(token=secret_code).first()
        # print(connection)

        if not connection:
            return jsonify({'status': 'error', 'message': _l('Invalid secret code. Please try again.')}), 400

        if connection.expires_at > datetime.utcnow():
            device: Device = db.session.query(Device).get(connection.class_id)
            if device.owner_id:
                return jsonify({"status": "error", "message": _l("Device already has owner")}), 404

            device.owner_id = current_user.id
            db.session.commit()

            return jsonify({'status': 'success', 'message': _l('Class added successfully!')}), 200
        else:
            connections: list[NewClassTokens] = NewClassTokens.query.where(NewClassTokens.expires_at <= datetime.utcnow()).all()
            for conn in connections:
                db.session.delete(conn)
            db.session.commit()
            return jsonify({'status': 'error', 'message': _l('Too old secret code')}), 404
    else:
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

            if len(cells) >= 30:
                return render_template('classes/users_limit.html'), 403
            if not user.phone:
                phone_history = PhoneHistory(user_id=user.id, history=json.dumps({}))
                db.session.add(phone_history)
                db.session.commit()
                user.phone = phone_history

            for cell in cells.values():
                if cell[0] == user.id:
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
            return render_template('errors/bad_link.html'), 403
    else:
        return render_template('errors/bad_link.html'), 403


# Remove user from class
@module.route('/class/<int:class_id>/remove/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user(class_id, user_id):
    device: Device = db.session.query(Device).get(class_id)

    if device.owner_id != current_user.id:
        return jsonify({'status': 'error', 'message': _l('Permission denied')}), 403

    cells = json.loads(device.cells)

    for cell, cell_data in cells.items():
        if cell_data[0] == user_id:
            del cells[cell]
            break

    device.cells = json.dumps(cells)

    db.session.commit()

    return jsonify({"status": "success", "device": device.name}), 200
