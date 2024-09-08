from flask import render_template

from . import module


# Create a settings page
@module.route('/')
def settings():
    return render_template('settings/settings.html', title='Settings')
