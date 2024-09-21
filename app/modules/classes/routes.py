import json

from flask import render_template
from flask_login import login_required, current_user

from . import module
from app import db
from app.models import Device


# Create "Your classes" page
@module.route('/')
@login_required
def classes():
    study_classes = current_user.get_classes()
    return render_template('classes/classes.html', title='Your phone', study_classes=study_classes)