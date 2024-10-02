from flask import render_template
from flask_babel import lazy_gettext as _l

from . import module


# Create a main page
@module.route('/')
def main():
    return render_template('main/main.html', title=_l('About Us'))
