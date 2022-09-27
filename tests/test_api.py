import bupytest
import requests


class TestAPI(bupytest.UnitTest):
    def __init__(self):
        super().__init__()
        
        base_url = 'http://127.0.0.1:5550/api'
        
        self._login_url = f'{base_url}/login'
        self._register_url = f'{base_url}/register'
        self._user_email = 'user@mail.com'
        self._user_password = 'secret-password'

    def test_register_user(self):
        register_data = {
            'email': self._user_email,
            'password': self._user_password
        }

        request = requests.post(self._register_url, json=register_data)
        self.assert_expected(request.status_code, 201)

        result = request.json()

        self.assert_expected(result.get('status'), 'success')
        self.assert_expected(result.get('message'), 'Account created')
        self.assert_true(result.get('token'))


if __name__ == '__main__':
    bupytest.this()
