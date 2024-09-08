from flask import render_template

from . import module


# Create "Your phone" page
@module.route('/')
def phone():
    return render_template('phone/phone.html')