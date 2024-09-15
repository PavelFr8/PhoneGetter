from flask import Blueprint

from app import csrf

module = Blueprint('api', __name__, url_prefix='/api')

csrf.exempt(module)

from app.api import errors, devices