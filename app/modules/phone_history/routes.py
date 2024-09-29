import json
from datetime import datetime

from flask import render_template
from flask_login import login_required, current_user

from . import module


# Create "Your phone" page
@module.route('/')
@login_required
def history():
    try:
        phone_history = json.loads(current_user.phone.history)

        filtered = {date: events for date, events in phone_history.items() if events is not None}

        filtered = dict(sorted(
            filtered.items(),
            key=lambda item: datetime.strptime(item[0], '%Y.%m.%d') if '.' in item[0] else float('inf'),
            reverse=True
        ))

        for val in filtered.values():
            val.sort(reverse=True)

        if not phone_history:
            filtered = None
    except Exception:
        filtered = None

    return render_template('phone/phone.html', history=filtered)