import os


class UserAuth:
    def _get_utoken_key(self) -> str:
        return os.environ.get('UTOKEN_KEY', 'secret-key')
