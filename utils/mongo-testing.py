from pymongo import MongoClient

client = MongoClient("mongodb://root:example@localhost:27017/")
db = client.mydatabase
users = db.users

for user in users.find():
    print(user)
