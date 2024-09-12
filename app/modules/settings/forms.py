from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired


class UserChangePasswordForm(FlaskForm):
    email = EmailField('Email')
    curr_password = PasswordField('Your password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    submit = SubmitField('Save')