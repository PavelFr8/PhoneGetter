import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from dotenv import load_dotenv

import logging


db = SQLAlchemy()  # create database
login_manager = LoginManager()  # create manager for login
csrf = CSRFProtect()  # create csrf protection

# create logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_app():
    # create Flask app
    app = Flask(__name__)

    # get from .env app settings
    load_dotenv()
    settings = os.environ.get('APP_SETTINGS')
    app.config.from_object(settings)

    if app.debug == True:
        try:
            toolbar = DebugToolbarExtension(app)
        except Exception as e:
            app.logger.error(f"Failed to initialize DebugToolbarExtension: {e}")

    # register API
    import app.api as api
    app.register_blueprint(api.module)

    # register errors handler
    import app.errors as errors
    app.register_blueprint(errors.module)

    # register all app modules
    import app.modules.main as main
    app.register_blueprint(main.module)

    import app.modules.settings as settings
    app.register_blueprint(settings.module)

    import app.modules.phone_history as phone_history
    app.register_blueprint(phone_history.module)

    import app.modules.classes as classes
    app.register_blueprint(classes.module)

    import app.modules.register as register
    app.register_blueprint(register.module)

    return app