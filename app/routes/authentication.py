from flask import request, jsonify, make_response
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
from bson import ObjectId
from constants import (
    USERNAME_EXISTS, USER_REGISTERED, AUTH_MISSING, AUTH_REALM,
    USER_NOT_FOUND, INVALID_PASSWORD, CREDENTIALS_UPDATED, NO_FIELDS_TO_UPDATE
)

def register(users):
    username = request.json.get('username')
    password = request.json.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if users.find_one({"username": username}):
        return jsonify({"message": USERNAME_EXISTS}), 400

    users.insert_one({"username": username, "password": hashed_password})
    return jsonify({"message": USER_REGISTERED}), 201

def login(users, app):
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response(AUTH_MISSING, 401, {'WWW-Authenticate': AUTH_REALM})

    user = users.find_one({"username": auth.get('username')})

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': AUTH_REALM})

    if bcrypt.checkpw(auth.get('password').encode('utf-8'), user['password']):
        user_id = str(user['_id'])  # Convert MongoDB ObjectId to string
        token = jwt.encode({'sub': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['JWT_EXPIRATION_MINUTES'])}, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return make_response(AUTH_MISSING,  401, {'WWW-Authenticate': AUTH_REALM})
