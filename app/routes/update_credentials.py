from flask import request, jsonify, make_response
import bcrypt
from bson import ObjectId
from utils.encrypt import validate_jwt
from constants import USER_NOT_FOUND, INVALID_PASSWORD, CREDENTIALS_UPDATED, NO_FIELDS_TO_UPDATE

def update_credentials(users, app):
    auth_token = request.headers.get('Authorization')
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if auth_token is None:
        return make_response(jsonify({"message": "Authorization token is missing"}), 401)

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    user_id = ObjectId(message['sub'])

    current_password = request.json.get('current_password')
    new_username = request.json.get('new_username')
    new_password = request.json.get('new_password')

    # Verificar que los campos obligatorios estén presentes
    if current_password is None:
        return jsonify({"message": "Current password is required"}), 400

    if new_username is None and new_password is None:
        return jsonify({"message": "Either new_username or new_password must be provided"}), 400

    user = users.find_one({"_id": user_id})

    if not user:
        return jsonify({"message": USER_NOT_FOUND}), 404

    if not bcrypt.checkpw(current_password.encode('utf-8'), user['password']):
        return jsonify({"message": INVALID_PASSWORD}), 401

    update_fields = {}

    # Verificar si el nuevo nombre de usuario ya existe
    if new_username:
        existing_user = users.find_one({"username": new_username})
        if existing_user and str(existing_user['_id']) != str(user_id):
            return jsonify({"message": "The username is already taken"}), 400
        update_fields["username"] = new_username

    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_fields["password"] = hashed_password

    if update_fields:
        users.update_one({"_id": user_id}, {"$set": update_fields})
        return jsonify({"message": CREDENTIALS_UPDATED}), 200

    return jsonify({"message": NO_FIELDS_TO_UPDATE}), 400
