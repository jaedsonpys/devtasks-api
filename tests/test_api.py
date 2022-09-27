import bupytest
import requests


class TestAPI(bupytest.UnitTest):
    def __init__(self):
        super().__init__()
        
        base_url = 'http://127.0.0.1:5550/api'
        self._login_url = f'{base_url}/login'
        self._register_url = f'{base_url}/register'


if __name__ == '__main__':
    bupytest.this()
