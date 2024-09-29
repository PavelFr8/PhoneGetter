from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class InviteForm(FlaskForm):
    invite_link = StringField('Invite Link', validators=[DataRequired()], render_kw={"readonly": True})

class SecretCodeForm(FlaskForm):
    secret_code = StringField('Secret Code', validators=[DataRequired()], render_kw={"placeholder": "Enter secret code"})