from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy as sa
import sqlalchemy.orm as orm

import datetime

from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    surname = sa.Column(sa.String, nullable=False)
    date_of_birth = sa.Column(sa.Date, nullable=False)
    email = sa.Column(sa.String, unique=True, nullable=False, index=True)
    hashed_password = sa.Column(sa.String, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def update_password(self, new_password):
        self.set_password(new_password)
