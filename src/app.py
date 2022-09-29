import hashlib
import os
import random

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
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        if original_pw == hashed_pw:
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


@app.route('/api/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
@user_auth.auth_required
def tasks(request, user_payload):
    if request.method == 'POST':
        task_data = request.json()

        if not task_data or not task_data.get('task_name'):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

        # getting task data
        task_name = task_data.get('task_name')
        task_id = random.randint(100000, 999999)
        task_status = 'incomplete'

        new_task = {
            'name': task_name,
            'id': task_id,
            'status': task_status
        }

        user_email = user_payload['email']

        tasks_list = db.get(f'users/{user_email}/tasks') or []
        tasks_list.append(new_task)

        db.add(f'users/{user_email}/tasks', tasks_list)

        response = {'status': 'success', 'message': 'Task added'}, 201

    return response


if __name__ == '__main__':
    import os

    port = os.environ.get('PORT', 5500)
    app.run(port=port)
