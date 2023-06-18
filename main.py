#!bin/bash
import jwt
import json
from flask import Flask, request, jsonify, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import pymongo
from bson import ObjectId
import bson
from logging_api.logs_api import LogSystem
from authentication.jwt_handler import token_required, generate_jwt, decode_jwt
from authentication.mail import Message, load_reset_template, MailServer, load_confirmation_template
from utils.request_data_handler import get_request_metadata
from utils.config_handler import read_json
from utils.time_functions import current_time
from utils.room_util_functions import generate_id
from database.database_api import DataabseAPI
import os
import threading

# Initialize flask instance of our application
app = Flask(__name__)

# Initialize the rate limit handler
limiter = Limiter(get_remote_address, app=app, default_limits=["1000 per day", "50 per hour"])

# Enable interaction with external components such as frontend
CORS(app)


# Reading Application configurations from configs.json file.
os.chdir(os.path.dirname(__file__))
config = read_json("configs.json")
SECRET_KEY = config["secret_key"]
TIME_WINDOW = config["time_window_in_minuts"]
DB_URI = config["DB_URI"]
DB_NAME = config["DB_NAME"]
BASE_FRONTEND_LINK = config["frontend_link"]

# Initialize database handler.
database_obj = DataabseAPI(DB_URI, DB_NAME)
log_obj = LogSystem()

@app.route("/api/v1/reset/<user_token>", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password(user_token) -> Response | tuple[Response, int] | str:
    external_addr, time_now = get_request_metadata()
    try:
        result = decode_jwt(SECRET_KEY, user_token)
        body = json.loads(request.data.decode())
        new_password = body["new_password"]
        if len(new_password) == 0 or len(new_password) > 50:
            return jsonify({"message": "Invalid password value can't be empty or more than 50 char.", "code": 400})
        user_id, topic = result["user_id"], result["topic"]
        if user_id == "":
            return jsonify({"message": "Invalid user id.", "code": 400})
        if topic == "reset-password":
            result = database_obj.updateRecord(
                ObjectId(user_id), {"password": new_password}, "Accounts")
            return jsonify({"message": "Password updated successfully", "code": 200})
    except (jwt.exceptions.InvalidAlgorithmError,           # altered hashing algorithm
            jwt.exceptions.DecodeError,                     # invalid token
            jwt.exceptions.InvalidSignatureError) as error: # invalid signature secret key
        return jsonify({"message": f"Invalid authentication token: {error}", "code": 400}), 400
    except KeyError as error:
        if str(error) == "'topic'":
            return jsonify({"message": f"Invalid authentication token: {error}", "code": 400}), 400
        else:
            return jsonify({"message": f"Missing required keys: {error}", "code": 400}), 400


@app.route("/api/v1/forget", methods=["POST"])
@limiter.limit("5 per minute")
def forget_password() -> tuple[Response, int]:
    try:
        body = json.loads(request.data.decode())
        user_email = body["email"]
        result = database_obj.getRecords({"email": user_email}, "Accounts")
        if len(result) == 0:
            return jsonify({"message": "Invalid email address", "code": 400}), 400
        else:
            first_name = result[0]["first_name"]
            # Generate token
            token = generate_jwt(SECRET_KEY,
                                30,
                                {"topic": "reset-password",
                                "user_id": str(result[0]["_id"])})
            email_server = MailServer()
            message_body = load_reset_template()
            # Form the reset email template
            message_body = message_body.replace("__EMAIL__", user_email)
            message_body = message_body.replace("__FIRST_NAME__", first_name)
            reset_url_link = BASE_FRONTEND_LINK + "/reset/" + \
                token + "&rwnc=qgelgl&pryqvmb=obpbqmxpptloa"
            message_body = message_body.replace("__LINK__", reset_url_link)
            message = Message("Reset email password", user_email, message_body)
            t1 = threading.Thread(target=email_server.send,
                              args=(message.get_message(),))
            t1.start()
            return jsonify({"message": "Check your inbox, if provided email is valid you will found the reset email.", "code": 200}), 200
    except KeyError as error:
        return jsonify({"message": f"Missing required keys: {error}", "code": 400}), 400
    except FileNotFoundError as error:
        log_obj.write_into_log("!", "reset_password_template is missing.")
        return jsonify({"message": f"Reset template not found.", "code": 400}), 400


@app.route("/api/v1/signin", methods=["POST"])
@limiter.limit("5 per minute")
def signin() -> Response:
    try:
        body = json.loads(request.data.decode())
        user_email = body["email"]
        user_password = body["password"]
        result = database_obj.getRecords(
            {"email": user_email, "password": user_password}, "Accounts")
        if len(result) == 0:
            return jsonify({"message": "Invalid credentials", "code": 400}), 400
        time_windo = 30*24*60 # thirty days in minutes
        token = generate_jwt(SECRET_KEY, time_windo, {
                            "user_id": str(result[0]["_id"])})
        return jsonify({"message": "User authenticated successfully", "token": token, "user_id": str(result[0]["_id"]), "code": 200}), 200
    except KeyError as error:
        return jsonify({"message": f"Missing required keys: {error}", "code": 400}), 400


@app.route("/api/v1/signup", methods=["POST"])
def signup():
    try:
        body = json.loads(request.data.decode())
        new_account = {
            "email": body["email"],
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
            "type": body["type"],
        }
        # Adding system fields
        new_account["creation_time"] = str(current_time())
        new_account["last_modification_time"] = str(current_time())

        # Handling Duplicate Accounts by the following lines
        # because Mongodb indexes are not working for no reason. :'(
        result = database_obj.getRecords({"email": body["email"]}, "Accounts")
        if len(result) == 0:
            # Adding account to database
            result = database_obj.createRecord(new_account, "Accounts")
        else:
            return jsonify({"message": f"Duplicated Account.", "code": 400}), 400 
        # Send confirmation email to email address
        email_server = MailServer()
        message_body = load_confirmation_template()
        message_body = message_body.replace(
            "__FIRST_NAME__", body["firstName"])
        token = generate_jwt(SECRET_KEY, 10, {"topic": "confirmation",
                                              "account_id": str(result),
                                              "email": body["email"]})
        conf_link = BASE_FRONTEND_LINK + "/confirmation/" + token + "&rwnc=pfdkrm"
        message_body = message_body.replace("__CONFIRMATION_LINK__", conf_link)
        message = Message("Confirmation Email", body["email"], message_body)
        t1 = threading.Thread(target=email_server.send,
                              args=(message.get_message(),))
        t1.start()
        return jsonify({"message": "Account created successfully.",
                        "account_id": str(result),
                        "code": 201}), 201
    except KeyError as error:
        return jsonify({"message": f"Missing required keys: {error}", "code": 400}), 400
    except FileNotFoundError:
        log_obj.write_into_log("!", "Confirmation_template is missing.")
        return jsonify({"message": f"Rconfirmation template not found.", "code": 400}), 400


@app.route("/api/v1/confirmation/gen", methods=["POST"])
@limiter.limit("5 per minute")
def generate_confirmation_token():
    try:
        body = json.loads(request.data.decode())
        account_id = body["account_id"]
        record = database_obj.getRecords({"_id": ObjectId(account_id)}, "Accounts")
        email = record[0]["email"]
        # check if account is new and not confirmed before that.
        if record[0]["is_confirmed"] == False:
            # generate a new confirmation token with new time window.
            token = generate_jwt(SECRET_KEY, 10, {"topic": "confirmation",
                                                "account_id": account_id,
                                                "email": email})
            conf_link = BASE_FRONTEND_LINK + "/confirmation/" + token + "&rwnc=pfdkrm"
            return jsonify({"message": "Link created successfully",
                            "confirmation_link": conf_link, "code": 200}), 200
        else:
            return jsonify({"message": "Account is already confirmed", "code": 400}), 400
    except KeyError as error:
        return jsonify({"message": f"Missing required keys: {error}", "code": 400}), 400
    except bson.errors.InvalidId:
        return jsonify({"message": f"Invalid account id", "code": 400}), 400


@app.route("/api/v1/confirmation/<token>", methods=["POST"])
def confirmation(token):
    try:
        result = decode_jwt(SECRET_KEY, token)
        account_id = result["account_id"]
        topic = result["topic"]
        # check if the token topic is for confirmation.
        if topic == "confirmation":
            account_record = database_obj.getRecordById(
                ObjectId(account_id), "Accounts")
            if len(account_record) == 0:
                return jsonify({"message": f"Invalid account id: {error}", "code": 400}), 400
            # check if the account is not confirmed.
            confirmation_status = account_record["is_confirmed"]
            if confirmation_status:
                return jsonify({"message": "This Account is already confirmed", "code": 400}), 400
            else:
                database_obj.updateRecord(ObjectId(account_id), {
                                          "is_confirmed": True}, "Accounts")
                return jsonify({"message": "Account confirmed successfully", "code": 200}), 200
    except KeyError as error:
        if str(error) == "'topic'":
            return jsonify({"message": f"Invalid authentication token: {error}", "code": 400}), 400
        else:
            return jsonify({"message": f"Missing required keys: {error}", "code": 400}), 400
    except Exception as error:
        return jsonify({"message": "Token expired!", "code": 400}), 400

# ================================================================= # 

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'), threaded=True) 

# لقطة الختاااام, مسك الختام, مسك الختااااااااام, خلااااااااص خلااااااااص خلااااااااااااااااص رضخت اخيرا
