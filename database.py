import os

import requests


class Database:
    def __init__(self) -> None:
        self.database_url = 'https://remote-cookiedb.herokuapp.com'
        self._database_pw = os.environ.get('DATABASE_PW')

        self._token = self._login()

    def _login(self) -> str:
        request = requests.get(self.database_url + '/login', params={'password': self.database_pw})

        if request.status_code == 401:
            raise ConnectionError('Invalid database API password')

        data = request.json()
        return data.get('token')
