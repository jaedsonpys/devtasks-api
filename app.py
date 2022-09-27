import hashlib

import utoken
from pysgi import PySGI
from cookiedb import CookieDB


app = PySGI()
db = CookieDB()

db.create_database('devtasks', if_not_exists=True)
db.open('devtasks')


@app.route('/api/register', methods=['POST'])
def register(request):
    data = request.json()

    if not data or not data.get('email') or not data.get('password'):
        return {'status': 'error', 'message': 'Invalid login JSON'}, 400

    email = data.get('email')
    password = data.get('password')

    user_exists = db.get(f'users/{email}')

    if not user_exists:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        db.add(
            path=f'users/{email}',
            value={
                'email': email,
                'password': hashed_pw
            }
        )

        response = {'status': 'success', 'message': 'Account created'}, 201
    else:
        response = {'status': 'error', 'message': 'User already exists'}, 409

    return response


if __name__ == '__main__':
    import os

    port = os.environ.get('PORT', 5500)
    app.run(port=port)
