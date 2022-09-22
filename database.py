import os


class Database:
    def __init__(self):
        os.environ.get('DATABASE_URL')
        os.environ.get('DATABASE_PW')
