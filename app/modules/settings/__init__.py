from flask import Blueprint

module = Blueprint('settings', __name__, url_prefix ='/settings')

from app.modules.settings import routes