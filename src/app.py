import secrets

import bcrypt
from cookiedb import CookieDB
from flask import Flask, after_this_request, request
from flask_cors import CORS
from flask_restful import Api, Resource

from auth import Auth
from config import enviroment

SECRET_KEY = enviroment['SECRET_KEY']
DATABASE_KEY = enviroment['DATABASE_KEY']
SERVER_PORT = enviroment['SERVER_PORT']

app = Flask(__name__)
cors = CORS(app, supports_credentials=True)
api = Api(app, prefix='/api')
auth = Auth()

db = CookieDB('devtasks', key=DATABASE_KEY)

app.config['SECRET_KEY'] = SECRET_KEY


def revoke_token(*tokens: str):
    blacklist = db.get('tokenBlacklist') or []
    blacklist.extend(tokens)
    db.add('tokenBlacklist', blacklist)


def token_in_blacklist(token: str):
    blacklist = db.get('tokenBlacklist') or []
    return token in blacklist


def set_refresh_token_cookie(token: str):
    @after_this_request
    def set_cookie(response):
        response.set_cookie(
            key='refreshToken', 
            value=token,
            samesite='None',
            max_age=2592000,
            httponly=True,
            secure=True
        )

        return response


class Register(Resource):
    def post(self):
        data = request.json

        if not data or not data.get('email') or not data.get('password'):
            return {'status': 'error', 'message': 'Invalid register JSON'}, 400

        email = data.get('email')
        password = data.get('password')
        user_exists = db.get(f'users/{email}')

        if not user_exists:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode(), salt).decode()
            access_token = auth.generate_access_token(email)
            refresh_token = auth.generate_refresh_token(email)
            set_refresh_token_cookie(refresh_token)

            db.add(path=f'users/{email}', value={
                'email': email,
                'password': hashed_pw
            })

            response = {
                'status': 'success',
                'message': 'Account created',
                'token': access_token
            }, 201
        else:
            response = {'status': 'error', 'message': 'User already exists'}, 409

        return response


class Login(Resource):
    def post(self):
        data = request.json

        if not data or not data.get('email') or not data.get('password'):
            return {'status': 'error', 'message': 'Invalid login JSON'}, 400

        email = data.get('email')
        password = data.get('password')
        user_data = db.get(f'users/{email}')

        if user_data:
            original_pw = user_data.get('password')
            has_valid_pw = bcrypt.checkpw(password.encode(), original_pw.encode())

            if has_valid_pw:
                access_token = auth.generate_access_token(email)
                refresh_token = auth.generate_refresh_token(email)
                set_refresh_token_cookie(refresh_token)

                response = {
                    'status': 'success',
                    'message': 'Login succesfully',
                    'token': access_token
                }, 201
            else:
                response = {'status': 'error', 'message': 'Email or password incorrect'}, 401
        else:
            response = {'status': 'error', 'message': 'Email or password incorrect'}, 401

        return response


class Refresh(Resource):
    def get(self):
        refresh_token = request.cookies.get('refreshToken')

        if refresh_token:
            payload = auth.has_valid_refresh_token(refresh_token)

            if payload and not token_in_blacklist(refresh_token):
                # generate a new access and refresh token
                new_access_token = auth.generate_access_token(payload['email'])
                new_refresh_token = auth.generate_refresh_token(payload['email'])

                # revoke previous refresh token
                revoke_token(refresh_token)
                set_refresh_token_cookie(new_refresh_token)

                response = {'token': new_access_token}, 201
            else:
                response = {'status': 'error', 'message': 'Invalid Refresh Token'}, 406
        else:
            response = {'status': 'error', 'message': 'Refresh token not available'}, 406

        return response


class Tasks(Resource):
    method_decorators = [auth.auth_required]

    def get(self, user_payload: dict):
        user_email = user_payload['email']
        tasks_list = db.get(f'users/{user_email}/tasks') or {}
        sort_tasks = {}

        if tasks_list.get('global'):
            sort_tasks = {'global': tasks_list.pop('global')}

        sort_tasks.update(tasks_list)
        return sort_tasks, 200

    def post(self, user_payload: dict):
        user_email = user_payload['email']
        task_data: dict = request.json

        task_name = task_data.get('name')
        task_tag = task_data.get('tag')

        if not task_data or not all([task_name, task_tag]):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

        task_id = secrets.token_hex(4)
        task_status = 'incomplete'

        new_task = {
            'id': task_id,
            'name': task_name,
            'status': task_status
        }

        if not db.get(f'users/{user_email}/tasks/{task_tag}'):
            db.add(f'users/{user_email}/tasks/{task_tag}', [])

        db.append(f'users/{user_email}/tasks/{task_tag}', new_task)
        return new_task, 201

    def put(self, user_payload: dict):
        user_email = user_payload['email']
        task_data: dict = request.json

        task_status = task_data.get('status')
        task_id = task_data.get('id')

        if not task_data or not all([task_status, task_id]):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

        updated_task = None
        tasks_list = db.get(f'users/{user_email}/tasks') or {}

        for task_tag, tasks in tasks_list.items():
            for index, task in enumerate(tasks):
                if task['id'] == task_id:
                    updated_task = {
                        'id': task_id,
                        'name': task['name'],
                        'status': task_status
                    }

                    tasks_list[task_tag].append(updated_task)
                    tasks_list[task_tag].pop(index)
                    break

        if updated_task:
            db.add(f'users/{user_email}/tasks', tasks_list)
            response = updated_task, 201
        else:
            response = {'status': 'error', 'message': 'Task ID not found'}, 404

        return response

    def delete(self, user_payload: dict):
        user_email = user_payload['email']
        task_data: dict = request.json

        if not task_data or not task_data.get('id'):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

        deleted_task = None
        task_id = task_data.get('id')
        tasks_list = db.get(f'users/{user_email}/tasks') or {}

        for task_tag, tasks in tasks_list.items():
            for index, task in enumerate(tasks):
                if task['id'] == task_id:
                    deleted_task = tasks_list[task_tag].pop(index)
                    break

        if deleted_task:
            if not len(tasks_list[task_tag]):
                tasks_list.pop(task_tag)

            db.add(f'users/{user_email}/tasks', tasks_list)
            response = {'status': 'success', 'message': f'Task #{task_id} deleted'}, 200
        else:
            response = {'status': 'error', 'message': 'Task ID not found'}, 404

        return response


# register resources
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Refresh, '/refreshToken')
api.add_resource(Tasks, '/tasks')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=bool(enviroment.get('DEBUG', False)))
