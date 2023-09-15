from flask import Flask
import os
from pymongo import MongoClient
from app.routes.authentication import register, login
from app.routes.sensitive_data import store_sensitive_data, retrieve_sensitive_data
from app.routes.update_credentials import update_credentials

app = Flask(__name__)
app.config.from_object('config')

# MongoDB Connection
MONGO_USER = os.environ.get('MONGO_USER') 
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD') 
MONGO_HOST = os.environ.get('MONGO_HOST')  
MONGO_PORT = os.environ.get('MONGO_PORT') 

client = MongoClient(
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/",
    maxPoolSize=50,
    wtimeout=2500
)

db = client.mydatabase
users = db.users
sensitive_data = db.sensitive_data
sensitive_data_relations = db.sensitive_data_relations

@app.route('/register', methods=['POST'])
def register_route():
    return register(users)

@app.route('/login', methods=['POST'])
def login_route():
    return login(users, app)

@app.route('/store-sensitive-data', methods=['POST'])
def store_sensitive_data_route():
    return store_sensitive_data(sensitive_data, sensitive_data_relations, app)

@app.route('/retrieve-sensitive-data', methods=['GET'])
def retrieve_sensitive_data_route():
    return retrieve_sensitive_data(sensitive_data, sensitive_data_relations, app)

@app.route('/update-credentials', methods=['PUT'])
def update_credentials_route():
    return update_credentials(users, app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
