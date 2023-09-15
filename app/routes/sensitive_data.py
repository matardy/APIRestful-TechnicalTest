from flask import request, jsonify, make_response
from uuid import uuid4
from utils.encrypt import generate_key, encrypt_data, validate_jwt, decrypt_data
from bson import ObjectId
from constants import DATA_STORED, DATA_NOT_FOUND, DATA_NOT_FOUND_TOKEN

def store_sensitive_data(sensitive_data, sensitive_data_relations, app):
    auth_token = request.headers.get('Authorization')
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    user_id = message['sub']  # Assuming the 'sub' (subject) of the JWT contains the user ID

    data = request.json.get('credit_card_number')
    key = generate_key()
    encrypted_data = encrypt_data(data, key)

    unique_token = str(uuid4())

    sensitive_data_id = sensitive_data.insert_one({
        'token': unique_token,
        'encrypted_data': encrypted_data,
        'encryption_key': key
    }).inserted_id

    sensitive_data_relations.insert_one({
        'user_id': user_id,
        'token': unique_token,
        'sensitive_data_id': sensitive_data_id
    })

    return jsonify({"message": DATA_STORED, "token": unique_token})

def retrieve_sensitive_data(sensitive_data, sensitive_data_relations, app):
    auth_token = request.headers.get('Authorization')
    
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if not is_valid:
        return jsonify({"message": message}), 401

    user_id = message['sub']  # Assuming the 'sub' (subject) of the JWT contains the user ID

    relation = sensitive_data_relations.find_one({"user_id": user_id})

    if not relation:
        return jsonify({"message": DATA_NOT_FOUND}), 404

    stored_data = sensitive_data.find_one({"_id": relation['sensitive_data_id']})

    if not stored_data:
        return jsonify({"message": DATA_NOT_FOUND_TOKEN}), 404

    decrypted_data = decrypt_data(stored_data['encrypted_data'], stored_data['encryption_key'])

    return jsonify({"decrypted_data": decrypted_data})
