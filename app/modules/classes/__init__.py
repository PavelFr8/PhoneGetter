from flask import Blueprint

module = Blueprint('classes', __name__, url_prefix ='/classes')

from app.modules.classes import routes