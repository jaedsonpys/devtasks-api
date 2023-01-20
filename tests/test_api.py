import bupytest
import requests

BASE_URL = 'http://127.0.0.1:5500/api'
LOGIN_URL = BASE_URL + '/login'
REFRESH_URL = BASE_URL + '/refreshToken'
REGISTER_URL = BASE_URL + '/register'


class TestAPI(bupytest.UnitTest):
    def __init__(self):
        super().__init__()

        self._user_email = 'user@mail.com'
        self._user_password = 'secret-password'
        self._token: str = None


if __name__ == '__main__':
    bupytest.this()
