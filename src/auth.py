import os
from datetime import datetime, timedelta
from functools import wraps

import utoken
from utoken import exceptions as u_exception


class UserAuth:
    def _get_utoken_key(self) -> str:
        return os.environ.get('UTOKEN_KEY', 'secret-key')

    def create_user_token(self, email: str) -> str:
        utoken_key = self._get_utoken_key()
        token_exp = datetime.now() + timedelta(minutes=5)

        auth_token = utoken.encode({'email': email, 'max-time': token_exp}, utoken_key)
        return auth_token

    def has_valid_token(self, token: str) -> bool:
        try:
            utoken.decode(token, self._get_utoken_key())
        except (u_exception.ExpiredTokenError, u_exception.InvalidKeyError,
                u_exception.InvalidTokenError, u_exception.InvalidContentTokenError):
            return False
        else:
            return True

    def auth_required(self, func):
        @wraps(func)
        def decorator(request, *args, **kwargs):
            authorization = request.headers.get('Authorization')

            if not authorization:
                return {'status': 'error', 'message': 'Unauthorized'}, 401

            auth_type, token = authorization.split(' ')

            if auth_type == 'Bearer':
                if not self.has_valid_token(token):
                    response = {'status': 'error', 'message': 'Invalid auth token'}, 401
                else:
                    response = func(request, *args, **kwargs)

                return response
            else:
                return {'status': 'error', 'message': 'Please use Bearer Token'}, 401

        return decorator
