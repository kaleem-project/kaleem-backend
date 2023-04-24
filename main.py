import json
from typing import Tuple

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from bson import ObjectId
from authentication.jwt_handler import token_required, generate_jwt, decode_jwt
from authentication.mail import Message, load_reset_template, MailServer
from utils.config_handler import read_json
from database.database_api import DataabseAPI
import os



# Initialize flask instance of our application
app = Flask(__name__)
# Enable interaction with external components such as frontend
CORS(app)

# Reading Application configurations
os.chdir(os.path.dirname(__file__))
config = read_json("configs.json")
SECRET_KEY = config["secret_key"]
TIME_WINDOW = config["time_window_in_days"]
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


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
