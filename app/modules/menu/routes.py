from flask import render_template

from . import module


# Create a main page
@module.route('/')
def index():
    return render_template('menu/tmp.html')
