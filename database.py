import os

import requests


class Database:
    def __init__(self) -> None:
        self.database_url = 'https://remote-cookiedb.herokuapp.com'
        database_pw = os.environ.get('DATABASE_PW')

        request = requests.get(self.database_url + '/login', params={'password': database_pw})

        if request.status_code == 401:
            raise ConnectionError('Invalid database API password')

        data = request.json()
        self._token = data.get('token')
