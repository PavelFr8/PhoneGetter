from flask import render_template
from flask_login import login_required

from . import module


# Create "Your phone" page
@module.route('/')
@login_required
def phone():
    return render_template('phone/phone.html')