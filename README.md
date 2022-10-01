# DevTasks API

API for using the **DevTasks** application, developed using the [PySGI](https://github.com/jaedsonpys/pysgi) framework and [CookieDB](https://github.com/jaedsonpys/cookiedb) in its database.

## Running API

To run the API, you only need to execute one command, but first, make sure you add the **necessary environment variables**:

- `UTOKEN_KEY`: Utoken key;
- `PORT`: PySGI port (to production).

## Routes

- `/api/register` (POST): Register new user;
- `/api/login` (POST): Login user;

- `/api/tasks` (POST): Create new task;
- `/api/tasks` (PUT): Update a task;
- `/api/tasks` (GET): Get a task list.