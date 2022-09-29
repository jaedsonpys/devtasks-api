import bupytest
import requests


class TestAPI(bupytest.UnitTest):
    def __init__(self):
        super().__init__()
        
        base_url = 'http://127.0.0.1:5500/api'
        
        self._login_url = f'{base_url}/login'
        self._register_url = f'{base_url}/register'
        self._tasks_url = f'{base_url}/tasks'

        self._user_email = 'user@mail.com'
        self._user_password = 'secret-password'

        self._token: str = None

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

    def test_register_exists_user(self):
        register_data = {
            'email': self._user_email,
            'password': self._user_password
        }

        request = requests.post(self._register_url, json=register_data)
        self.assert_expected(request.status_code, 409)

        result = request.json()

        self.assert_expected(result.get('status'), 'error')
        self.assert_expected(result.get('message'), 'User already exists')
        self.assert_false(result.get('token'))

    def test_login_user(self):
        login_data = {
            'email': self._user_email,
            'password': self._user_password
        }

        request = requests.post(self._login_url, json=login_data)
        self.assert_expected(request.status_code, 201)

        result = request.json()

        self.assert_expected(result.get('status'), 'success')
        self.assert_expected(result.get('message'), 'Login succesfully')
        self.assert_true(result.get('token'))

        self._token = result.get('token')

    def test_add_task(self):
        task_data = {'task_name': 'programming in python'}
        headers = {'Authorization': f'Bearer {self._token}'}

        request = requests.post(self._tasks_url, json=task_data, headers=headers)
        self.assert_expected(request.status_code, 201)

        result = request.json()

        self.assert_expected(result.get('status'), 'success')
        self.assert_expected(result.get('message'), 'Task added')

    def test_add_task_2(self):
        task_data = {'task_name': 'work in devtasks'}
        headers = {'Authorization': f'Bearer {self._token}'}

        request = requests.post(self._tasks_url, json=task_data, headers=headers)
        self.assert_expected(request.status_code, 201)

        result = request.json()

        self.assert_expected(result.get('status'), 'success')
        self.assert_expected(result.get('message'), 'Task added')


if __name__ == '__main__':
    bupytest.this()
