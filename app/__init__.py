import os
import sys

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_wtf import CSRFProtect

from dotenv import load_dotenv
from loguru import logger

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()

# Setup logger
logger.remove()
logger.add(
    "app.log",
    level="DEBUG",
    rotation="10 MB",
    compression="zip"
)
logger.add(
    sys.stdout,
    level="DEBUG"
)

def create_app():
    """
    Factory function to create a Flask application.
    """
    app = Flask(__name__)

    # get from .env app settings
    load_dotenv()
    settings = os.environ.get('APP_SETTINGS')
    app.config.from_object(settings)

    # Log application startup
    logger.info("Starting Flask application...")

    if app.debug == True:
        try:
            DebugToolbarExtension(app)
        except Exception as e:
            logger.error(f"Failed to initialize DebugToolbarExtension: {e}")

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

    logger.info("Flask application initialized successfully.")

    return app
