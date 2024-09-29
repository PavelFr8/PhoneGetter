from datetime import datetime
import json

from flask import request, render_template, redirect, url_for
from flask_login import current_user, login_required

from app.models import User
from app import db, logger
from . import module
from .forms import UserChangePasswordForm


# Create a settings page
@module.route('/')
@login_required
def settings():
    try:
        history = json.loads(current_user.phone.history)
        history = {date: events for date, events in history.items() if events is not None}
        filtered = dict()
        for item in history.items():
            if datetime.strptime(item[0], '%Y.%m.%d') == datetime.strptime(datetime.strftime(datetime.now(), "%Y.%m.%d"), '%Y.%m.%d'):
                filtered[item[0]] = item[1]
        if not history:
            filtered = None
    except Exception:
        filtered = None
    return render_template('settings/settings.html', title='Settings', history=filtered)

# Update user password
@module.route('/change_password/<int:id>', methods=['GET', 'POST'])
@login_required
def change_password(id: int):
    form = UserChangePasswordForm()
    try:
        user: User = current_user
        if request.method == 'GET':
            form.email.data = user.email

        elif form.validate_on_submit():
            if user.check_password(form.curr_password.data):
                user.set_password(form.new_password.data)
                db.session.commit()
                # flash('Пароль успешно изменен!', 'success')
                return redirect(url_for('settings.settings'))
            else:
                form.email.data = user.email
                return render_template('settings/change_password.html', title='Ваш профиль', form=form, message='Passwords are different.')

    except Exception as e:
        logger.error(f"Error changing password for user {id}: {e}")
        db.session.rollback()
        return render_template('settings/change_password.html', title='Ваш профиль', form=form, message='Error, please retry.')

    return render_template('settings/change_password.html', title='Ваш профиль', form=form)
