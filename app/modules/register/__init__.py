from flask import Blueprint

module = Blueprint('register', __name__, url_prefix ='/register')

from app.modules.register import routes