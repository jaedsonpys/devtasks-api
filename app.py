import hashlib
import os

from cookiedb import CookieDB
from pysgi import PySGI

from auth import UserAuth

app = PySGI()
user_auth = UserAuth()
db = CookieDB()

db.create_database('devtasks', if_not_exists=True)
db.open('devtasks')


@app.route('/api/register', methods=['POST'])
def register(request):
    data = request.json()

    if not data or not data.get('email') or not data.get('password'):
        return {'status': 'error', 'message': 'Invalid register JSON'}, 400

    email = data.get('email')
    password = data.get('password')

    user_exists = db.get(f'users/{email}')

    if not user_exists:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        auth_token = user_auth.create_user_token(email)

        db.add(
            path=f'users/{email}',
            value={
                'email': email,
                'password': hashed_pw
            }
        )

        register_data = {
            'status': 'success',
            'message': 'Account created',
            'token': auth_token
        }

        response = register_data, 201
    else:
        response = {'status': 'error', 'message': 'User already exists'}, 409

    return response


@app.route('/api/login', methods=['POST'])
def login(request):
    data = request.json()

    if not data or not data.get('email') or not data.get('password'):
        return {'status': 'error', 'message': 'Invalid login JSON'}, 400

    email = data.get('email')
    password = data.get('password')

    user_data = db.get(f'users/{email}')

    if user_data:
        original_pw = user_data.get('password')

        hashed_original_pw = hashlib.sha256(original_pw.encode()).hexdigest()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        if hashed_original_pw == hashed_pw:
            auth_token = user_auth.create_user_token(email)

            login_data = {
                'status': 'success',
                'message': 'Login succesfully',
                'token': auth_token
            }

            response = login_data, 201
        else:
            response = {'status': 'error', 'message': 'Email or password incorrect'}, 401
    else:
        response = {'status': 'error', 'message': 'Email or password incorrect'}, 401

    return response


if __name__ == '__main__':
    import os

    port = os.environ.get('PORT', 5500)
    app.run(port=port)
