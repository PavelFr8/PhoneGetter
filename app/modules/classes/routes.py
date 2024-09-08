from flask import render_template

from . import module


# Create "Your classes" page
@module.route('/')
def classes():
    return render_template('classes/classes.html', title='Your phone')