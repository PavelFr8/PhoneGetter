from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l

from wtforms import PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired



class UserChangePasswordForm(FlaskForm):
    email = EmailField(_l('Email'))
    curr_password = PasswordField(_l('Your current password'), validators=[DataRequired()])
    new_password = PasswordField(_l('New password'), validators=[DataRequired()])
    submit = SubmitField(_l('Save'))
