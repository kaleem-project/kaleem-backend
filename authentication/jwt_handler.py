import json
import jwt
from functools import wraps
from flask import Flask, request, jsonify
import datetime
import json
import os

secret = "5a26829c32d8d2e27330612f4270ffef62e0ef200a6f634d3a7009b8dbdf434e"

def generate_jwt(secret: str, time_window: int, payload: dict) -> str:
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=time_window)
    payload["expiration_time"] = expiration_time.timestamp()
    token = jwt.encode(payload, secret)
    return token


def decode_jwt(secret_key: str, request_token: str) -> dict:
    data = jwt.decode(request_token, secret_key, algorithms=['HS256'])
    return data


def token_required(func):
    """Function to validate the passed token in the HTTP request"""
    @wraps(func)
    def decorated(*args, **kwargs):
        jwt_token = ""
        content_type = ""
        try:
            jwt_token = request.headers["Authorization"]
            content_type = request.headers["Content-Type"]
        except KeyError:
            if len(jwt_token) == 0 or len(content_type) == 0:
                return jsonify({'Alert!': 'Authorization/Content-Type header is missing!'}), 401
        try:
            jwt_token = jwt_token.split(" ")[1]
            x = decode_jwt(secret, jwt_token)
        except Exception as error_message:
            print(error_message)
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated
