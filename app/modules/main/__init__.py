from flask import Blueprint

module = Blueprint('main', __name__, url_prefix ='/')

from app.modules.main import routes