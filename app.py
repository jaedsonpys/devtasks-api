from pysgi import PySGI
from cookiedb import CookieDB

import utoken

app = PySGI()
db = CookieDB()


if __name__ == '__main__':
    import os

    port = os.environ.get('PORT', 5500)
    app.run(port=port)
