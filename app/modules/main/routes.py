from flask import render_template

from . import module


# Create a main page
@module.route('/')
def main():
    return render_template('main/main.html', title='About Us')
