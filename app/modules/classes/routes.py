from flask import render_template
from flask_login import login_required, current_user

from . import module
from app import db
from app.models import Device


# Create "Your classes" page
@module.route('/')
@login_required
def classes():
    try:
        study_classes = current_user.get_classes()
    except Exception:
        study_classes = None
    return render_template('classes/classes.html', title='Your phone', study_classes=study_classes)

# Create "Your classes" page
@module.route('/new')
@login_required
def add_new_class():
    return render_template('classes/classes.html', title='Your phone')


@module.route('/class/<int:id>')
@login_required
def study_class(id):
    phone_class = db.session.query(Device).filter(Device.id == id).first()
    return render_template('classes/classes.html', title='', study_class=phone_class)