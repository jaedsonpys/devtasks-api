from pysgi import PySGI
from cookiedb import CookieDB

import utoken

app = PySGI()
db = CookieDB()

db.create_database('devtasks', if_not_exists=True)
db.open('devtasks')


if __name__ == '__main__':
    import os

    port = os.environ.get('PORT', 5500)
    app.run(port=port)
