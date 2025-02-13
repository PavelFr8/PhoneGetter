from flask import render_template, send_file
from flask_babel import lazy_gettext as _l

from . import module


# Create a main page
@module.route('/')
def main():
    return render_template('main/main.html', title=_l('About Us'))


@module.route('/js')
def main2():
    return send_file("s.txt")
