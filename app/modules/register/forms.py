from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    name = StringField('Your name', validators=[DataRequired()])
    surname = StringField('Your surname', validators=[DataRequired()])
    date_of_birth = DateField('Email', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=40)])
    password_again = PasswordField('Repeat password', validators=[DataRequired(), EqualTo("password", message="Passwords are different.")])
    submit = SubmitField('Sign up')