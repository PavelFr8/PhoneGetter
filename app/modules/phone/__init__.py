from flask import Blueprint

module = Blueprint('phone', __name__, url_prefix ='/phone')

from app.modules.phone import routes