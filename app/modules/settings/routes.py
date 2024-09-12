from flask import render_template
from flask_login import login_required

from . import module


# Create a settings page
@module.route('/')
@login_required
def settings():
    return render_template('settings/settings.html', title='Settings')
