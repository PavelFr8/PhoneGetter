import json
import uuid
from datetime import datetime, timedelta
import pytz

from flask_login import UserMixin
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy as sa
import sqlalchemy.orm as orm

from app import db


# User class with authentication capabilities
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    surname = sa.Column(sa.String, nullable=False)
    date_of_birth = sa.Column(sa.Date, nullable=False)
    email = sa.Column(sa.String, unique=True, nullable=False, index=True)
    hashed_password = sa.Column(sa.String, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.utcnow())
    utc = sa.Column(sa.String, default='')

    # Relationships: One-to-many with Device, one-to-one with PhoneHistory
    device = orm.Relationship("Device", back_populates="owner")
    phone = orm.Relationship("PhoneHistory", back_populates="user", uselist=False)

    # Set and hash password for the user
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # Check password for authentication
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    # Update user's password
    def update_password(self, new_password):
        self.set_password(new_password)

    # Retrieve and parse device classes for the user
    def get_classes(self):
        classes = db.session.query(Device).filter(Device.owner_id == self.id).all()
        if classes:
            for device in classes:
                device.cells = json.loads(device.cells)
                device.phones = 0
                for val in device.cells.values():
                    if val[1] == True:
                        device.phones += 1
            return classes
        else:
            return None


# Device class representing devices owned by users
class Device(db.Model):
    __tablename__ = "devices"

    # json_default = json.dumps({f'{cell}': ["user_id", "state"] for cell in range(1, 31)})

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    ip = sa.Column(sa.String, nullable=False, unique=True)
    cells = sa.Column(sa.JSON, nullable=True, default=json.dumps({}))
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    # Relationship: Device belongs to one user
    owner = orm.Relationship('User', back_populates='device', uselist=False)

    # API token for the device
    api_token = sa.Column(sa.String, unique=True, nullable=False, index=True)

    # Method to generate API token
    def generate_api_token(self):
        self.api_token = generate_password_hash(f"{int(uuid.uuid4())}" + str(datetime.utcnow()), method='pbkdf2:sha256')
        db.session.commit()
        return self.api_token


# PhoneHistory class to track user's phone usage or history
class PhoneHistory(db.Model):
    __tablename__ = "phone_history"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    history = sa.Column(sa.JSON, nullable=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    # Relationship: One-to-one with User
    user = orm.Relationship('User', back_populates='phone', uselist=False)

    # Method to update phone history
    def update_history(self, action):
        # Load the existing history JSON
        self.history = json.loads(self.history) if self.history else {}

        # Get the current time in UTC
        current_utc_time = datetime.now(pytz.UTC)

        # Get the user's timezone using Flask-Babel
        tzname = self.user.utc
        if tzname:
            tzname = pytz.timezone(tzname)
        else:
            tzname = pytz.UTC

        user_timezone = tzname

        # Convert UTC time to user's timezone
        current_time_user = current_utc_time.astimezone(user_timezone)

        # Format the date and time according to the user's timezone
        formatted_date = current_time_user.strftime("%d.%m.%Y")
        formatted_time = current_time_user.strftime("%H:%M")

        # Save the action and the formatted timestamp
        action = (action, f"{formatted_date} {formatted_time}")
        today = current_time_user.strftime("%Y.%m.%d")

        # Update the history for today or create a new entry
        if today in self.history:
            self.history[today].append(action)
        else:
            self.history[today] = [action]

        # Keep history for the last 30 days
        thirty_days_ago = (current_utc_time - timedelta(days=30)).strftime("%Y.%m.%d")
        self.history = {date: actions for date, actions in self.history.items() if date >= thirty_days_ago}

        # Save history as JSON string
        self.history = json.dumps(self.history)


# PhoneHistory class keeps secret tokens to make adding students to class safe
class InviteLink(db.Model):
    __tablename__ = "invite_link"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))


# PhoneHistory class keeps secret tokens to make adding students to class safe
class NewClassTokens(db.Model):
    __tablename__ = "new_class_tokens"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: (datetime.utcnow() + timedelta(minutes=10)))