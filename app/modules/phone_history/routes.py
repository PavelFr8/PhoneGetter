import json
from datetime import datetime

from flask import render_template
from flask_login import login_required, current_user

from . import module
from app import db
from app.models import User


# Create "Your phone" page
@module.route('/')
@login_required
def history():
    phone_history = json.loads(current_user.phone.history)

    phone_history = {date: events for date, events in phone_history.items() if events is not None}

    phone_history = dict(sorted(
        phone_history.items(),
        key=lambda item: datetime.strptime(item[0], '%Y.%m.%d') if '.' in item[0] else float('inf'),
        reverse=True
    ))
    return render_template('phone/phone.html', history=phone_history)