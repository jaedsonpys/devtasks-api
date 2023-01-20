import random

import bupytest
import requests

BASE_URL = 'http://127.0.0.1:5500/api'
LOGIN_URL = BASE_URL + '/login'
REFRESH_URL = BASE_URL + '/refreshToken'
REGISTER_URL = BASE_URL + '/register'


class TestAPI(bupytest.UnitTest):
    def __init__(self):
        super().__init__()

        self.access_token: str = None
        self.refresh_token: str = None

        email_id = random.randint(1000, 9999)
        email = f'dev{email_id}@mail.com'
        password = str(random.randint(10000, 99999))

        self.login_data = {
            'email': email,
            'password': password
        }

        self.incorrect_login_data = {
            'email': email,
            'password': 'fake-password'
        }

        self.register_data = self.login_data.copy()


if __name__ == '__main__':
    bupytest.this()
