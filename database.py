import os

import requests


class Database:
    def __init__(self):
        database_url = 'https://remote-cookiedb.herokuapp.com'
        database_pw = os.environ.get('DATABASE_PW')
