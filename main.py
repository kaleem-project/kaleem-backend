import json
from typing import Tuple
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from bson import ObjectId
from authentication.jwt_handler import token_required, generate_jwt, decode_jwt
from authentication.mail import Message, load_reset_template, MailServer, load_confirmation_template
from utils.config_handler import read_json
from utils.time_functions import current_time
from database.database_api import DataabseAPI
import os
import threading

# Initialize flask instance of our application
app = Flask(__name__)
# Enable interaction with external components such as frontend
CORS(app)

# Reading Application configurations
os.chdir(os.path.dirname(__file__))
config = read_json("configs.json")
SECRET_KEY = config["secret_key"]
TIME_WINDOW = config["time_window_in_minuts"]
DB_URI = config["DB_URI"]
DB_NAME = config["DB_NAME"]
database_obj = DataabseAPI(DB_URI, DB_NAME)


@app.route("/api/v1/auth", methods=["GET"])
def auth() -> Response:
    body = json.loads(request.data.decode())
    if "username" in body.keys() and "password" in body.keys():
        username, password = body["username"], body["password"]
        db_obj = DataabseAPI(DB_URI, DB_NAME)
        # search for this username in db
        result = db_obj.getRecords({"username": username, "password": password}, "Accounts")
        if len(result) == 1:
            user_map = {"id": str(result[0]["_id"]), "email": str(result[0]["email"]), "topic": "login"}
            token = generate_jwt(SECRET_KEY, TIME_WINDOW, user_map)
            return jsonify({"data": {"token": token}, "code": 200})
        else:
            return jsonify({"message": "<username> or <password> is incorrect", "code": 400})
    else:
        return jsonify({"message": "<username> or <password> key is missing", "code": 400})

@app.route("/api/v1/reset/<user_token>", methods=["GET"])
def reset_password(user_token) -> Response | tuple[Response, int] | str:
    try:
        result = decode_jwt(SECRET_KEY, user_token)
        body = json.loads(request.data.decode())
        new_password = body["new_password"]
        user_id, topic = result["user_id"], result["topic"]
        if topic == "reset-password" and user_id != "":
            result = database_obj.updateRecord(ObjectId(user_id),{"password": new_password},"Accounts")
            return jsonify({"message": "Password updated successfully", "code": 200})
    except:
        return jsonify({"message": "Invalid authentication token", "code": 400}), 400
    return ""

@app.route("/api/v1/forget", methods=["GET"])
def forget_password() -> tuple[Response, int]:
    body = json.loads(request.data.decode())
    print(body)
    user_email = body["email"]
    result = database_obj.getRecords({"email": user_email}, "Accounts")
    if len(result) == 0:
        return jsonify({"message": "Invalid email address", "code": 400}), 400
    else:
        first_name = result[0]["firstName"]
        email_server = MailServer()
        message_body = load_reset_template()
        message = Message("Reset email password", user_email, message_body)
        email_server.send(message.get_message())
        return jsonify({"message": "We have send reset password link to your email","code": 200}), 200


@app.route("/api/v1/signin", methods=["POST"])
def check_user() -> dict:
    # try:
    body = json.loads(request.data.decode())
    user_email = body["email"]
    user_password = body["password"]
    result = database_obj.getRecords({"email": user_email, "password": user_password}, "Accounts")
    if len(result) == 0:
        return jsonify({"message": "Invalid credentials", "code": 400}), 400
    thirty_days_in_min = 30*24*60 
    token = generate_jwt(SECRET_KEY, thirty_days_in_min, {"user_id": str(result[0]["_id"])})
    return jsonify({"message": "user authenticated successfully", "token": token, "user_id": str(result[0]["_id"]), "code": 200}), 200


@app.route("/api/v1/signup", methods=["POST"])
def signup():
    body = json.loads(request.data.decode())
    try:
        new_account = {
            "username": body["username"],
            "email": body["email"],
            "username": body["username"],
            "password": body["password"],
            "first_name": body["firstName"],
            "last_name": body["lastName"],
            "headLine": body["headLine"],
            "gender": body["gender"],
            "is_active": True,
            "is_confirmed": False,
            "profile_image": body["profileImage"],
            "country": body["country"],
            "first_login": True,
        }
        # Adding system fields
        new_account["creation_time"] = str(current_time())
        new_account["last_modification_time"] = str(current_time())
        # Adding account to database
        result = database_obj.createRecord(new_account, "Accounts")
        # Send confirmation email to email address
        email_server = MailServer()
        message_body = load_confirmation_template()
        message_body = message_body.replace("__FIRST_NAME__", body["firstName"])
        token = generate_jwt(SECRET_KEY, 10, {"topic": "confirmation",
                                             "account_id": str(result),
                                             "email": body["email"]})
        conf_link = "https://127.0.0.1:5000/api/v1/confirmation/" + token
        message_body = message_body.replace("__CONFIRMATION_LINK__", conf_link)
        message = Message("Confirmation Email", body["email"], message_body)
        # email_server.send(message.get_message())
        t1 = threading.Thread(target=email_server.send, args=(message.get_message(),))
        t1.start()
        return jsonify({"message": "Account created successfully and mail sent",
                    "account_id": 123,
                    "code": 201}), 201
    except Exception as DuplicateKeyError:
        return jsonify({"message": "Duplicated email or username", "code": 400}), 400


@app.route("/api/v1/confirmation/gen", methods=["GET"])
def generate_confirmation_token():
    body = json.loads(request.data.decode())
    account_id = body["account_id"]
    record = database_obj.getRecords({"_id": ObjectId(account_id)}, "Accounts")
    email = record[0]["email"]
    if record[0]["is_confirmed"] == False:
        token = generate_jwt(SECRET_KEY, 10, {"topic": "confirmation",
                                            "account_id": account_id,
                                            "email": email})
        conf_link = "https://127.0.0.1:5000/api/v1/confirmation/" + token
        return jsonify({"message": "Account is already confirmed", 
                        "confirmation_link": conf_link, "code": 200}), 200
    else:
        return jsonify({"message": "Account is already confirmed", "code": 400}), 400


@app.route("/api/v1/confirmation/<token>", methods=["GET"])
def confirmation(token):
    try:
        result = decode_jwt(SECRET_KEY, token)
        account_id = result["account_id"]
        topic = result["topic"]
        if topic == "confirmation":
            database_obj.updateRecord(ObjectId(account_id), {"is_confirmed": True}, "Accounts")
    except Exception as error:
        return jsonify({"message": "Token expired!","code": 400}), 400
    return jsonify({"message": "Account confirmed successfully","code": 200}), 200


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
