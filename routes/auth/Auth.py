from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from models.entities.User import User
from models.UserModel import UserModel

main = Blueprint('auth_blueprint', __name__)


@main.route('/login', methods=['POST'])
def login():
    try:
        email = request.json['email']
        password = request.json['password']
        return UserModel.login_user(email, password)
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='login'), 500


@main.route('/register', methods=['POST'])
def register():
    try:
        id = request.json['id']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        email = request.json['email']
        password = request.json['password']

        hash_password = generate_password_hash(password)

        user = User(id, first_name, last_name,  email, hash_password)

        affected_rows = UserModel.register_user(user)

        if affected_rows == 1:
            return jsonify(status=200,
                           data=user.email), 200
        else:
            return jsonify(status=500, message='Failed to insert', method='register'), 500

    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='register'), 500
