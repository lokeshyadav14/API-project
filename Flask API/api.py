from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

# Establish a connection to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["users"]

# Initialize a counter for user IDs
user_id_counter = 1

# Define a parser for user input
user_parser = reqparse.RequestParser()
user_parser.add_argument("name", type=str, required=True, help="Name is required")
user_parser.add_argument("email", type=str, required=True, help="Email is required")
user_parser.add_argument("password", type=str, required=True, help="Password is required")

# Custom error handling
def abort_if_user_not_found(user_id):
    user = collection.find_one({"id": user_id})
    if not user:
        abort(404, message=f"User with ID {user_id} not found")

class UserResource(Resource):
    def get(self, user_id):
        user_id = int(user_id)  # Convert to integer
        abort_if_user_not_found(user_id)
        user = collection.find_one({"id": user_id}, {"_id": 0})
        return user

    def put(self, user_id):
        user_id = int(user_id)  # Convert to integer
        abort_if_user_not_found(user_id)
        args = user_parser.parse_args()
        collection.update_one({"id": user_id}, {"$set": args})
        return {"message": "User updated successfully"}

    def delete(self, user_id):
        user_id = int(user_id)  # Convert to integer
        abort_if_user_not_found(user_id)
        collection.delete_one({"id": user_id})
        return {"message": "User deleted successfully"}

class UserListResource(Resource):
    def get(self):
        users = list(collection.find({}, {"_id": 0}))
        return users

    def post(self):
        args = user_parser.parse_args()
        global user_id_counter
        args["id"] = user_id_counter  # Assign a simple number as ID
        user_id_counter += 1  # Increment the counter
        collection.insert_one(args)
        return {"message": "User created successfully", "id": args["id"]}, 201

api.add_resource(UserResource, "/users/<string:user_id>")
api.add_resource(UserListResource, "/users")

if __name__ == "__main__":
    app.run(debug=True)
