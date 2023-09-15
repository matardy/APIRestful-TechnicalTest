from flask import request, jsonify, make_response
from utils.encrypt import validate_jwt
from utils.s3_operations import upload_file_to_s3, generate_presigned_url
from bson import ObjectId

S3_BUCKET = 'profile-pictures-techtest'

def upload_profile_picture(users, app):
    auth_token = request.headers.get('Authorization')
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])
    
    if auth_token is None:
        return make_response(jsonify({"message": "Authorization token is missing"}), 401)

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    # Asumo que la imagen se envía como un archivo en una solicitud multipart
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    success, filename_or_message = upload_file_to_s3(file, S3_BUCKET, object_name=f"profile_pictures/{file.filename}")

    if success:
        # Actualizar el campo 'profile_picture' en MongoDB
        users.update_one(
            {'_id': ObjectId(message['sub'])},
            {'$set': {'profile_picture': f"profile_pictures/{file.filename}"}}  # Usar el nombre del archivo real
        )
        return jsonify({"message": "Profile picture uploaded and user updated.", "filename": file.filename}), 200  # Usar el nombre del archivo real
    else:
        return jsonify({"message": f"Failed to upload: {filename_or_message}"}), 500

def get_profile_picture_url(users, app):
    auth_token = request.headers.get('Authorization')
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])
    
    if auth_token is None:
        return make_response(jsonify({"message": "Authorization token is missing"}), 401)

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    user_id = message['sub']
    user = users.find_one({'_id': ObjectId(user_id)})
    if not user or 'profile_picture' not in user:
        return jsonify({"message": "User not found or profile picture not set"}), 404

    success, url_or_message = generate_presigned_url(S3_BUCKET, user['profile_picture'])
    if success:
        return jsonify({"message": "URL generated", "url": url_or_message}), 200
    else:
        return jsonify({"message": f"Failed to generate URL: {url_or_message}"}), 500



