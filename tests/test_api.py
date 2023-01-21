import random

import bupytest
import requests

BASE_URL = 'http://127.0.0.1:5500/api'

LOGIN_URL = BASE_URL + '/login'
REFRESH_URL = BASE_URL + '/refreshToken'
REGISTER_URL = BASE_URL + '/register'
TASKS_URL = BASE_URL + '/tasks'


class TestAPI(bupytest.UnitTest):
    def __init__(self):
        super().__init__()

        self.access_token: str = None
        self.refresh_token: str = None
        self.old_refresh_token: str = None

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

        try:
            requests.get(BASE_URL)
        except requests.exceptions.ConnectionError:
            print('API not available to test')
            exit(0)

    def _get_auth(self):
        return {'Authorization': f'Bearer {self.access_token}'}

    def test_register(self):
        response = requests.post(REGISTER_URL, json=self.register_data)
        self.assert_expected(response.status_code, 201)

        data = response.json()

        self.assert_expected(data.get('status'), 'success')
        self.assert_true(response.cookies.get('refreshToken'))
        self.assert_true(data.get('token'))

    def test_register_same_user(self):
        response = requests.post(REGISTER_URL, json=self.register_data)
        self.assert_expected(response.status_code, 409)

        data = response.json()

        self.assert_expected(data.get('status'), 'error')
        self.assert_false(data.get('token'))

    def test_login(self):
        response = requests.post(LOGIN_URL, json=self.login_data)
        self.assert_expected(response.status_code, 201)

        data = response.json()

        refresh_token = response.cookies.get('refreshToken')
        access_token = data.get('token')

        self.access_token = access_token
        self.refresh_token = refresh_token

        self.assert_expected(data.get('status'), 'success')
        self.assert_true(refresh_token)
        self.assert_true(access_token)

    def test_login_with_incorrect_data(self):
        response = requests.post(LOGIN_URL, json=self.incorrect_login_data)
        self.assert_expected(response.status_code, 401)

        data = response.json()

        refresh_token = response.cookies.get('refreshToken')
        access_token = data.get('token')

        self.assert_expected(data.get('status'), 'error')
        self.assert_false(refresh_token)
        self.assert_false(access_token)

    def test_refresh_token(self):
        response = requests.get(REFRESH_URL, cookies={'refreshToken': self.refresh_token})
        self.assert_expected(response.status_code, 201)

        data = response.json()

        refresh_token = response.cookies.get('refreshToken')
        access_token = data.get('token')

        self.assert_true(self.refresh_token != refresh_token)
        self.assert_true(refresh_token)
        self.assert_true(access_token)

        self.old_refresh_token = self.refresh_token
        self.access_token = access_token
        self.refresh_token = refresh_token

    def test_refresh_with_old_token(self):
        response = requests.get(REFRESH_URL, cookies={'refreshToken': self.old_refresh_token})
        self.assert_expected(response.status_code, 406)

        data = response.json()

        self.assert_expected(data['status'], 'error')
        self.assert_expected(data['message'], 'Invalid Refresh Token')

    def test_tasks_endpoint_without_auth(self):
        response = requests.get(TASKS_URL)
        self.assert_expected(response.status_code, 401)
        data = response.json()
        self.assert_expected(data['status'], 'error')
        self.assert_expected(data['message'], 'Unauthorized')

    def test_add_task(self):
        task = {'name': 'My Task'}
        response = requests.post(TASKS_URL, json=task, headers=self._get_auth())
        self.assert_expected(response.status_code, 201)

        data = response.json()

        self.assert_expected(data.get('name'), 'My Task')
        self.assert_expected(data.get('status'), 'incomplete')
        self.assert_true(data.get('id'))

    def test_get_tasks(self):
        response = requests.get(TASKS_URL, headers=self._get_auth())
        self.assert_expected(response.status_code, 200)

        data = response.json()

        self.assert_expected(len(data), 1)
        self.assert_expected(data[0]['name'], 'My Task')
        self.assert_expected(data[0]['status'], 'incomplete')
        self.assert_true(data[0]['id'])

        self._task_id = data[0]['id']

    def test_update_task_status(self):
        data = {'id': self._task_id, 'status': 'complete'}
        response = requests.put(TASKS_URL, json=data, headers=self._get_auth())
        self.assert_expected(response.status_code, 201)

        data = response.json()

        self.assert_expected(len(data), 3)
        self.assert_expected(data['name'], 'My Task')
        self.assert_expected(data['status'], 'complete')
        self.assert_expected(data['id'], self._task_id)

    def test_delete_task(self):
        data = {'id': self._task_id}
        response = requests.delete(TASKS_URL, json=data, headers=self._get_auth())
        self.assert_expected(response.status_code, 200)
        data = response.json()
        self.assert_expected(data.get('status'), 'success')

    def test_get_tasks_2(self):
        response = requests.get(TASKS_URL, headers=self._get_auth())
        self.assert_expected(response.status_code, 200)

        data = response.json()
        self.assert_expected(len(data), 0)


if __name__ == '__main__':
    bupytest.this()
