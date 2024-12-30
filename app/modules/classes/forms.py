from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l

from wtforms import StringField
from wtforms.validators import DataRequired

class InviteForm(FlaskForm):
    invite_link = StringField(_l('Invite Link'), validators=[DataRequired()], render_kw={"readonly": True})

class SecretCodeForm(FlaskForm):
    secret_code = StringField(_l('Secret Code'), validators=[DataRequired()], render_kw={"placeholder": _l("Enter secret code")})

class ChangeClassNameForm(FlaskForm):
    invite_link = StringField(_l('Change Name'), validators=[DataRequired()], render_kw={"placeholder": _l("Enter new name")})
