from flask_login import LoginManager, AnonymousUserMixin
from database.model import UserModel

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.filter(UserModel.id == user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
    return {'success': False, 'message': 'Authorization required'}, 401

