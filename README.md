# DevTasks API

API for using the **DevTasks** application, developed using the [Flask](https://github.com/pallets/flask) framework and [CookieDB](https://github.com/jaedsonpys/cookiedb) in its database.

## Running API

To run the API, you only need to execute one command, but first, make sure you add the **necessary environment variables**:

- `UTOKEN_KEY`: Utoken key;
- `PORT`: Server port (to production).

## Routes

- `/api/register` (POST): Register new user;
- `/api/login` (POST): Login user;

- `/api/tasks` (POST): Create new task;
- `/api/tasks` (PUT): Update a task;
- `/api/tasks` (GET): Get a task list.

# License

```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
```

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
