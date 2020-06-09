from flask import Flask, redirect, request, jsonify, session, render_template
from flask_login import login_required, current_user, login_user, logout_user
from flask_restplus import Namespace, Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from database.model import UserModel


api = Namespace('user', description='User related operations')

register = reqparse.RequestParser()
register.add_argument('username', required=True, location='form')
register.add_argument('password', required=True, location='form')
# register.add_argument('email', location='json')
# register.add_argument('name', location='json')

login = reqparse.RequestParser()
login.add_argument('password', required=True, location='form')
login.add_argument('username', required=True, location='form')

set_password = reqparse.RequestParser()
set_password.add_argument('password', required=True, location='json')
set_password.add_argument('new_password', required=True, location='json')



@api.route('/login')
class UserLogin(Resource):
    @api.expect(login)
    def post(self):
        """ Logs user in """
        args = login.parse_args()
        username = args.get('username')
        user = UserModel.query.filter(UserModel.username == username).first()

        if user is None:
            return {'success': False, 'message': 'Could not authenticate user'}, 400

        if check_password_hash(user.password, args.get('password')):
            login_user(user)
        # if user.password == args.get('password'):
        #     login_user(user)
            return {'success': True, 'user': current_user.id}
            # if current_user.is_authenticated:
            #     return {'success': True, "user": current_user.username}
        return {'success': False, 'message': 'Could not authenticate user'}, 400


@api.route('/logout')
class UserLogout(Resource):
    @login_required
    def get(self):
        logout_user()
        return {'success': True}


@api.route('/register')
class UserRegister(Resource):
    @api.expect(register)
    def post(self):
        """ Creates user """

        # users = User.objects.count()

        args = register.parse_args()
        username = args.get('username')

        if UserModel.query.filter(UserModel.username == username).first():
            return {'success': False, 'message': 'Username already exists.'}, 400

        user = UserModel()
        user.username = args.get('username')
        user.password = generate_password_hash(args.get('password'), method='sha256')

        user.save()

        login_user(user)

        return {'success': True, 'user': current_user.username}

# if __name__ == '__main__':          #建立项目时选择了flask项目，此处不会直接执行这个py文件，而是递交给flask框架去执行
#     app.run(host="0.0.0.0")