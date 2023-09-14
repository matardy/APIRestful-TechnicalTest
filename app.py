from flask import Flask, jsonify, request, make_response
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
import uuid
from flask import request, jsonify, make_response
from uuid import uuid4
import jwt
from bson import ObjectId


from utils.encrypt import generate_key, decrypt_data, encrypt_data, validate_jwt

# Conexión a MongoDB y selección de colecciones
#TODO: Manejar Mongo en un script diferente
client = MongoClient("mongodb://root:example@mongo:27017/")
db = client.mydatabase
users = db.users
sensitive_data = db.sensitive_data
sensitive_data_relations = db.sensitive_data_relations  # Nueva colección para relaciones


app = Flask(__name__)
app.config.from_object('config')


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if users.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 400

    users.insert_one({"username": username, "password": hashed_password})
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = users.find_one({"username": auth.get('username')})

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if bcrypt.checkpw(auth.get('password').encode('utf-8'), user['password']):
        user_id = str(user['_id'])  # Convert MongoDB ObjectId to string
        token = jwt.encode({'sub': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=app.app_contextconfig['JWT_EXPIRATION_MINUTES'])}, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return make_response('Could not verify',  401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/store-sensitive-data', methods=['POST'])
def store_sensitive_data():
    # Validar el token JWT del usuario
    auth_token = request.headers.get('Authorization')
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    user_id = message['sub']  # Asumiendo que el 'sub' (subject) del JWT contiene el ID del usuario

    # Continuar con el almacenamiento de datos sensibles
    data = request.json.get('credit_card_number')
    key = generate_key()
    encrypted_data = encrypt_data(data, key)

    # Generar un token único para esta entrada
    unique_token = str(uuid4())

    # Almacenar datos cifrados y token en MongoDB
    sensitive_data_id = sensitive_data.insert_one({
        'token': unique_token,
        'encrypted_data': encrypted_data,
        'encryption_key': key
    }).inserted_id

    # Añadir una nueva entrada en la colección de relaciones
    sensitive_data_relations.insert_one({
        'user_id': user_id,
        'token': unique_token,
        'sensitive_data_id': sensitive_data_id
    })

    return jsonify({"message": "Data stored successfully", "token": unique_token})


@app.route('/retrieve-sensitive-data', methods=['GET'])
def retrieve_sensitive_data():
    auth_token = request.headers.get('Authorization')
    
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if not is_valid:
        return jsonify({"message": message}), 401

    user_id = message['sub']  # Asumiendo que el 'sub' (subject) del JWT contiene el ID del usuario

    # Buscar la relación en la colección de relaciones
    relation = sensitive_data_relations.find_one({"user_id": user_id})

    if not relation:
        return jsonify({"message": "No data found for the given user"}), 404

    # Buscar en MongoDB usando el sensitive_data_id
    stored_data = sensitive_data.find_one({"_id": relation['sensitive_data_id']})

    if not stored_data:
        return jsonify({"message": "No data found for the given token"}), 404

    # Descifrar datos
    decrypted_data = decrypt_data(stored_data['encrypted_data'], stored_data['encryption_key'])

    return jsonify({"decrypted_data": decrypted_data})

@app.route('/update-credentials', methods=['PUT'])
def update_credentials():
    # Validar el token JWT del usuario
    auth_token = request.headers.get('Authorization')
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    # Mongo espera que el campo sea un objeto ObjectID, basicamente un objeto de 12 bytes, no un str:python
    user_id = ObjectId(message['sub'])
    #user_id = message['sub']  # Asumiendo que el 'sub' (subject) del JWT contiene el ID del usuario

    # Obtener los campos del cuerpo de la petición
    current_password = request.json.get('current_password')
    new_username = request.json.get('new_username')
    new_password = request.json.get('new_password')

    # Buscar el usuario en MongoDB
    user = users.find_one({"_id": user_id})

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Verificar que las credenciales actuales sean correctas
    if not bcrypt.checkpw(current_password.encode('utf-8'), user['password']):
        return jsonify({"message": "Current password is incorrect"}), 401

    # Actualizar el nombre de usuario y/o la contraseña si se proporcionan
    update_fields = {}
    if new_username:
        update_fields["username"] = new_username
    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_fields["password"] = hashed_password

    if update_fields:
        users.update_one({"_id": user_id}, {"$set": update_fields})
        return jsonify({"message": "Credentials updated successfully"}), 200

    return jsonify({"message": "No fields to update"}), 400


@app.route('/')
def hello_world():
    # Obtener el token JWT de la cabecera "Authorization"
    auth_token = request.headers.get('Authorization')

    # Comprobar si el token existe
    if auth_token is None:
        return make_response(jsonify({"message": "Authorization token is missing"}), 401)

    # Validar el token utilizando la función existente
    is_valid, message = validate_jwt(auth_token, app.config['SECRET_KEY'])

    if not is_valid:
        return make_response(jsonify({"message": message}), 401)

    return jsonify(message="Hello, World!")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
