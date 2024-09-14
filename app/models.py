import json
from datetime import datetime, timedelta
import time

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy as sa
import sqlalchemy.orm as orm

from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    surname = sa.Column(sa.String, nullable=False)
    date_of_birth = sa.Column(sa.Date, nullable=False)
    email = sa.Column(sa.String, unique=True, nullable=False, index=True)
    hashed_password = sa.Column(sa.String, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.utcnow())

    device = orm.Relationship("Device", back_populates="owner")
    phone = orm.Relationship("User", back_populates="user", uselist=False)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def update_password(self, new_password):
        self.set_password(new_password)

    def get_classes(self):
        classes = db.session.query(Device).filter(Device.owner_id == self.id).all()
        if classes:
            for elem in classes:
                elem.cells = json.loads(elem.cells)
            return classes
        else:
            return False


class Device(db.Model):
    __tablename__ = "devices"

    json_default = json.dumps({str(i): (None, None) for i in range(1, 31)})

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    ip = sa.Column(sa.String, nullable=False)
    cells = sa.Column(sa.JSON, nullable=False, default=json_default)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    owner = orm.Relationship('User', back_populates='device', uselist=False)


class PhoneHistory(db.Model):
    __tablename__ = "phonehistory"

    json_default = json.dumps({str(i): None for i in range(1, 31)})

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    history = sa.Column(sa.JSON, nullable=False, default=json_default)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    user = orm.Relationship('User', back_populates='phone', uselist=False)

    def update_history(self, action):
        self.history = json.loads(self.history)
        action = (action, str(datetime.now().strftime("%d.%m.%Y") + " " + time.strftime("%H:%M")))
        today = datetime.now().strftime("%Y.%m.%d")

        if today in self.history:
            self.history[today].append(action)
        else:
            self.history[today] = [action]

        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y.%m.%d")
        self.history = {date: actions for date, actions in self.history.items() if date >= thirty_days_ago}

        self.history = json.dumps(self.history)







