from flask import render_template
from flask_login import login_required

from . import module


# Create "Your classes" page
@module.route('/')
@login_required
def classes():
    return render_template('classes/classes.html', title='Your phone')