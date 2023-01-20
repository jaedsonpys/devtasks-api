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
cors = CORS(app)
api = Api(app, prefix='/api')
auth = Auth()

app.config['SECRET_KEY'] = SECRET_KEY

db = CookieDB(key=DATABASE_KEY)
db.create_database('devtasks', if_not_exists=True)
db.open('devtasks')


def set_refresh_token_cookie(token: str):
    @after_this_request
    def set_cookie(response):
        response.set_cookie(
            key='refreshToken', 
            value=token,
            samesite='Strict',
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
        payload = auth.has_valid_refresh_token(refresh_token)

        if payload:
            access_token = auth.generate_access_token(payload['email'])
            response = {'token': access_token}
        else:
            response = {'status': 'error', 'message': 'Invalid Refresh Token'}, 406

        return response


class Tasks(Resource):
    method_decorators = [auth.auth_required]

    def get(self, user_payload: dict):
        user_email = user_payload['email']
        tasks_list = db.get(f'users/{user_email}/tasks') or []
        return tasks_list, 200

    def post(self, user_payload: dict):
        user_email = user_payload['email']
        task_data = request.json

        if not task_data or not task_data.get('task_name'):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

        # getting task data
        task_name = task_data.get('task_name')
        task_id = secrets.token_hex(4)
        task_status = 'incomplete'

        new_task = {
            'name': task_name,
            'id': task_id,
            'status': task_status
        }

        tasks_list = db.get(f'users/{user_email}/tasks') or []
        tasks_list.append(new_task)
        db.add(f'users/{user_email}/tasks', tasks_list)

        return new_task, 201

    def put(self, user_payload: dict):
        user_email = user_payload['email']
        task_data = request.json

        if not task_data or not task_data.get('task_status') or not task_data.get('task_id'):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

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
            response = updated_task, 201
        else:
            response = {'status': 'error', 'message': 'Task ID not found'}, 404

        return response

    def delete(self, user_payload: dict):
        user_email = user_payload['email']
        task_data = request.json

        if not task_data or not task_data.get('task_id'):
            return {'status': 'error', 'message': 'Invalid task data'}, 400

        deleted_task = None
        task_id = task_data.get('task_id')
        tasks_list = db.get(f'users/{user_email}/tasks') or []

        for index, task in enumerate(tasks_list):
            if task['id'] == task_id:
                deleted_task = tasks_list.pop(index)
                break

        if deleted_task:
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
    app.run(host='0.0.0.0', port=SERVER_PORT)
