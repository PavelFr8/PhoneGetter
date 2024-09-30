from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l

from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = EmailField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Log in'))


class RegisterForm(FlaskForm):
    name = StringField(_l('Your name'), validators=[DataRequired()])
    surname = StringField(_l('Your surname'), validators=[DataRequired()])
    date_of_birth = DateField(_l('Date'), validators=[DataRequired()])
    email = EmailField(_l('Email'), validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=6, max=40)])
    password_again = PasswordField(_l('Repeat password'), validators=[DataRequired(),
        EqualTo("password", message=_l("Passwords are different."))])
    submit = SubmitField(_l('Sign up'))
