from datetime import timedelta
from functools import wraps
from typing import Union

import utoken
from flask import jsonify, request
from utoken import exceptions as u_exception

from config import enviroment

REFRESH_EXP_TIME = timedelta(days=30)
ACCESS_EXP_TIME = timedelta(minutes=5)

REFRESH_TOKEN_KEY = enviroment['REFRESH_TOKEN_KEY']
ACCESS_TOKEN_KEY = enviroment['ACCESS_TOKEN_KEY']


class Auth:
    def generate_user_token(self, email: str) -> str:
        token = utoken.encode(
            payload={'email': email},
            key=ACCESS_TOKEN_KEY,
            expires_in=ACCESS_EXP_TIME
        )

        return token

    def generate_refresh_token(self, email: str) -> str:
        token = utoken.encode(
            payload={'email': email},
            key=REFRESH_TOKEN_KEY,
            expires_in=REFRESH_EXP_TIME
        )

        return token

    def has_valid_user_token(self, token: str) -> Union[bool, dict]:
        try:
            payload = utoken.decode(token, ACCESS_TOKEN_KEY)
        except (u_exception.ExpiredTokenError, u_exception.InvalidKeyError,
                u_exception.InvalidTokenError, u_exception.InvalidContentTokenError):
            return False
        else:
            return payload

    def has_valid_refresh_token(self, token: str) -> Union[bool, dict]:
        try:
            payload = utoken.decode(token, REFRESH_TOKEN_KEY)
        except (u_exception.ExpiredTokenError, u_exception.InvalidKeyError,
                u_exception.InvalidTokenError, u_exception.InvalidContentTokenError):
            return False
        else:
            return payload

    def auth_required(self, func):
        @wraps(func)
        def decorator():
            authorization = request.headers.get('Authorization')

            if authorization:
                try:
                    auth_type, token = authorization.split(' ')
                except ValueError:
                    response = jsonify({'status': 'error', 'message': 'Please use Bearer Token'}), 401
                else:
                    if auth_type == 'Bearer':
                        valid_token = self.has_valid_user_token(token)
                        if not valid_token:
                            response = jsonify({'status': 'error', 'message': 'Invalid auth token'}), 401
                        else:
                            response = func(valid_token)
                    else:
                        response = jsonify({'status': 'error', 'message': 'Please use Bearer Token'}), 401
            else:
                response = jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            return response

        return decorator
