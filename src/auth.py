import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Union

import utoken
from flask import jsonify, request
from utoken import exceptions as u_exception


class UserAuth:
    def _get_utoken_key(self) -> str:
        return os.environ.get('UTOKEN_KEY', 'secret-key')

    def generate_user_token(self, email: str) -> str:
        utoken_key = self._get_utoken_key()
        token_exp = datetime.now() + timedelta(days=1)

        auth_token = utoken.encode({'email': email, 'max-time': token_exp}, utoken_key)
        return auth_token

    def generate_refresh_token(self, email: str) -> str:
        utoken_key = self._get_utoken_key()
        refresh_token = utoken.encode({'email': email}, utoken_key)
        return refresh_token

    def has_valid_token(self, token: str) -> Union[bool, dict]:
        try:
            payload = utoken.decode(token, self._get_utoken_key())
        except (u_exception.ExpiredTokenError, u_exception.InvalidKeyError,
                u_exception.InvalidTokenError, u_exception.InvalidContentTokenError):
            return False
        else:
            return payload

    def auth_required(self, func):
        @wraps(func)
        def decorator():
            authorization = request.headers.get('Authorization')

            if not authorization:
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            auth_type, token = authorization.split(' ')

            if auth_type == 'Bearer':
                valid_token = self.has_valid_token(token)
                if not valid_token:
                    response = jsonify({'status': 'error', 'message': 'Invalid auth token'}), 401
                else:
                    response = func(valid_token)

                return response
            else:
                return jsonify({'status': 'error', 'message': 'Please use Bearer Token'}), 401

        return decorator
