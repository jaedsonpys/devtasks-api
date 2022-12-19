import hashlib
import os
import random

from cookiedb import CookieDB
from flask import Flask, jsonify, request
from flask import Response
from flask_cors import CORS

from auth import UserAuth

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')
DATABASE_KEY = os.environ.get('DATABASE_KEY')

app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = SECRET_KEY

user_auth = UserAuth()
db = CookieDB(key=DATABASE_KEY)

db.create_database('devtasks', if_not_exists=True)
db.open('devtasks')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'status': 'error', 'message': 'Invalid register JSON'}), 400

    email = data.get('email')
    password = data.get('password')

    user_exists = db.get(f'users/{email}')

    if not user_exists:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        auth_token = user_auth.generate_user_token(email)
        refresh_token = user_auth.generate_refresh_token(email)

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

        response = Response(jsonify(register_data), status=201)
        response.set_cookie('rftk', refresh_token, httponly=True)
    else:
        response = jsonify({'status': 'error', 'message': 'User already exists'}), 409

    return response


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'status': 'error', 'message': 'Invalid login JSON'}), 400

    email = data.get('email')
    password = data.get('password')

    user_data = db.get(f'users/{email}')

    if user_data:
        original_pw = user_data.get('password')
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        if original_pw == hashed_pw:
            auth_token = user_auth.generate_user_token(email)
            refresh_token = user_auth.generate_refresh_token(email)

            login_data = {
                'status': 'success',
                'message': 'Login succesfully',
                'token': auth_token
            }

            response = Response(jsonify(login_data), status=201)
            response.set_cookie('rftk', refresh_token, httponly=True)
        else:
            response = jsonify({'status': 'error', 'message': 'Email or password incorrect'}), 401
    else:
        response = jsonify({'status': 'error', 'message': 'Email or password incorrect'}), 401

    return response


@app.route('/api/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('rftk')
    payload = user_auth.has_valid_token(refresh_token)

    if payload:
        auth_token = user_auth.generate_user_token(payload['email'])
        return {'token': auth_token}
    else:
        return {'status': 'error', 'message': 'Invalid Refresh Token'}, 406


@app.route('/api/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
@user_auth.auth_required
def tasks(user_payload):
    user_email = user_payload['email']

    if request.method == 'GET':
        tasks_list = db.get(f'users/{user_email}/tasks') or []
        response = jsonify(tasks_list), 200
    elif request.method == 'POST':
        task_data = request.json

        if not task_data or not task_data.get('task_name'):
            return jsonify({'status': 'error', 'message': 'Invalid task data'}), 400

        # getting task data
        task_name = task_data.get('task_name')
        task_id = random.randint(100000, 999999)
        task_status = 'incomplete'

        new_task = {
            'name': task_name,
            'id': task_id,
            'status': task_status
        }

        tasks_list = db.get(f'users/{user_email}/tasks') or []
        tasks_list.append(new_task)

        db.add(f'users/{user_email}/tasks', tasks_list)

        response = jsonify(new_task), 201
    elif request.method == 'PUT':
        task_data = request.json

        if not task_data or not task_data.get('task_status') or not task_data.get('task_id'):
            return jsonify({'status': 'error', 'message': 'Invalid task data'}), 400

        task_status = task_data.get('task_status')
        task_id = task_data.get('task_id')
        updated_task = None

        tasks_list = db.get(f'users/{user_email}/tasks') or []

        for index, task in enumerate(tasks_list):
            if task['id'] == task_id:
                updated_task = {
                    'name': task['name'],
                    'id': task_id,
                    'status': task_status
                }

                tasks_list.pop(index)
                break

        if updated_task:
            tasks_list.append(updated_task)
            db.add(f'users/{user_email}/tasks', tasks_list)
            response = jsonify(updated_task), 201
        else:
            response = jsonify({'status': 'error', 'message': 'Task ID not found'}), 404
    elif request.method == 'DELETE':
        task_data = request.json

        if not task_data or not task_data.get('task_id'):
            return jsonify({'status': 'error', 'message': 'Invalid task data'}), 400

        task_id = task_data.get('task_id')
        deleted_task = None

        tasks_list = db.get(f'users/{user_email}/tasks') or []

        for index, task in enumerate(tasks_list):
            if task['id'] == task_id:
                deleted_task = tasks_list.pop(index)
                break

        if deleted_task:
            db.add(f'users/{user_email}/tasks', tasks_list)
            response = jsonify({'status': 'success', 'message': f'Task #{task_id} deleted'}), 200
        else:
            response = jsonify({'status': 'error', 'message': 'Task ID not found'}), 404

    return response


if __name__ == '__main__':
    key = os.environ.get('UTOKEN_KEY', 'secret-key')
    port = os.environ.get('PORT', 5500)

    if key == 'secret-key':
        print('\033[1;31mWARNING: PLEASE DEFINE A REAL SECRET KEY!\033[m')

    app.run(host='0.0.0.0', port=port)
