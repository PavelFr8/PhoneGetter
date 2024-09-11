from flask import render_template, make_response, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

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
        if form.password.data != form.password_again.data:
            return render_template('register/register.html', title='Sign Up', form=form,
                                   message='Passwords are different!')
        if User.query.filter_by(email=form.email.data).first():
            return render_template('register/register.html', title='Sign Up', form=form,
                                   message='User already exist')

        try:
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                date_of_birth=form.date_of_birth.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('register.login'))
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            db.session.rollback()
            return render_template('register/register.html', title='Регистрация', form=form,
                                   message='Произошла ошибка при регистрации.')

    return render_template('register/register.html', title='Регистрация', form=form)


# Logging
@module.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return make_response(redirect(url_for('settings.settings')))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                response = make_response(redirect(url_for('settings.settings')))
                # flash('Вы успешно вошли!', 'success')
                return response

            return render_template('register/login.html', title='Sign In', message='Mistake in login or password',
                                   form=form)
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return render_template('register/login.html', title='Sign Up', form=form,
                                   message='Error in authorisation.')

    return render_template('register/login.html', title='Authorisation', form=form)


# Logout
@module.route('/logout')
@login_required
def logout():
    logout_user()
    response = make_response(redirect(url_for('main.main')))
    response.set_cookie('username', '', expires=0)

    return response