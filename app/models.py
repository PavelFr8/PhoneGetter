import json
import uuid
from datetime import datetime, timedelta
import time

from flask_login import UserMixin
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
                    if val[0] == 1:
                        device.phones += 1
            return classes
        else:
            return None


# Device class representing devices owned by users
class Device(db.Model):
    __tablename__ = "devices"

    json_default = json.dumps({f'{cell}': ["user_id", "state"] for cell in range(1, 31)})

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    ip = sa.Column(sa.String, nullable=False, unique=True)
    cells = sa.Column(sa.JSON, nullable=False, default=json_default)
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
    __tablename__ = "phonehistory"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    history = sa.Column(sa.JSON, nullable=False, default=None)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    # Relationship: One-to-one with User
    user = orm.Relationship('User', back_populates='phone', uselist=False)

    # Method to update phone history
    def update_history(self, action):
        self.history = json.loads(self.history)

        # Add new action with timestamp
        action = (action, str(datetime.now().strftime("%d.%m.%Y") + " " + time.strftime("%H:%M")))
        today = datetime.now().strftime("%Y.%m.%d")

        if today in self.history:
            self.history[today].append(action)
        else:
            self.history[today] = [action]

        # Keep history for only the last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y.%m.%d")
        self.history = {date: actions for date, actions in self.history.items() if date >= thirty_days_ago}

        self.history = json.dumps(self.history)
