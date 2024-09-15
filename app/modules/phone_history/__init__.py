from flask import Blueprint

module = Blueprint('phone_history', __name__, url_prefix ='/phone_history')

from app.modules.phone_history import routes