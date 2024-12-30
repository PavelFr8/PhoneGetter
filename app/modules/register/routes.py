from flask import render_template, make_response, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from flask_babel import lazy_gettext as _l

from app.models import User
from app import db, logger
from . import module
from .forms import RegisterForm, LoginForm


# Registration user profile
@module.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return make_response(redirect(url_for('settings.settings')))

    form = RegisterForm()
    if form.validate_on_submit():
        logger.debug(f"Processing registration form for email: {form.email.data}")
        if form.password.data != form.password_again.data:
            return render_template('register/register.html', title=_l('Sign Up'), form=form,
                                   message=_l('Passwords are different!'))
        if User.query.filter_by(email=form.email.data).first():
            return render_template('register/register.html', title=_l('Sign Up'), form=form,
                                   message=_l('User already exists'))

        try:
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                date_of_birth=form.date_of_birth.data,
                email=form.email.data,
                utc=request.cookies.get('timezone')
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            logger.info(f"User {form.email.data} successfully registered.")
            return redirect(url_for('register.login'))
        except Exception as e:
            logger.error(f"Error registering user with email {form.email.data}: {e}")
            db.session.rollback()
            return render_template('register/register.html', title=_l('Registration'), form=form,
                                   message=_l('An error occurred during registration.'))

    return render_template('register/register.html', title=_l('Registration'), form=form)


# Logging
@module.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return make_response(redirect(url_for('settings.settings')))

    form = LoginForm()
    if form.validate_on_submit():
        logger.debug(f"Processing login form for email: {form.email.data}")
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                response = make_response(redirect(url_for('settings.settings')))
                return response

            return render_template('register/login.html', title=_l('Sign In'), message=_l('Mistake in login or password'),
                                   form=form)
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return render_template('register/login.html', title=_l('Sign Up'), form=form,
                                   message=_l('Error in authorization.'))

    return render_template('register/login.html', title=_l('Authorization'), form=form)


# Logout
@module.route('/logout')
@login_required
def logout():
    logout_user()
    response = make_response(redirect(url_for('main.main')))
    response.set_cookie('username', '', expires=0)

    return response
