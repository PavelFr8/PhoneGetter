from flask_migrate import Migrate

from app import create_app, db, login_manager, csrf
from app.models import User
# from app.models import User


app = create_app()

db.init_app(app)
with app.test_request_context():
    db.create_all()


migrate = Migrate(app, db)

# init login manager
login_manager.init_app(app)

# init CSRF protection
csrf.init_app(app)

# настройка передачи залогиненных пользователей

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user