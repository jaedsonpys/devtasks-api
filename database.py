import os

import requests


class Database:
    def __init__(self) -> None:
        self._cookiedb_api = 'https://remote-cookiedb.herokuapp.com'
        self._database_url = self._cookiedb_api + '/database'

        self._token = self._login()

    def _login(self) -> str:
        database_pw = os.environ.get('DATABASE_PW')
        request = requests.get(self._cookiedb_api + '/login', params={'password': database_pw})

        if request.status_code == 401:
            raise ConnectionError('Invalid database API password')

        data = request.json()
        return data.get('token')

    def check_user_exists(self, email: str) -> bool:
        json_data = {
            'path': f'devtasks/users/{email}'
        }

        headers = {
            'Authorization': f'Bearer {self._token}'
        }

        request = requests.get(self._database_url, headers=headers, json=json_data)
        user_exists = False

        if request.status_code == 401:
            self._token = self._login()
            request = requests.get(self._database_url, headers=headers, json=data)

            if request.status_code == 200:
                data = request.json()
                result = data.get('result')

                if result:
                    user_exists = result
        elif request.status_code == 200:
            data = request.json()
            result = data.get('result')

            if result:
                user_exists = True

        return user_exists

    def get_tasks(self) -> dict:
        data = {
            'path': 'devtasks/tasks/'
        }

        headers = {
            'Authorization': f'Bearer {self._token}'
        }

        request = requests.get(self._database_url, headers=headers, json=data)
        tasks = {}

        if request.status_code == 401:
            self._token = self._login()
            request = requests.get(self._database_url, headers=headers, json=data)

            if request.status_code == 200:
                data = request.json()
                result = data.get('result')

                if result:
                    tasks = result
        elif request.status_code == 200:
            data = request.json()
            result = data.get('result')

            if result:
                tasks = result

        return tasks
