from pysgi import PySGI
from database import Database

app = PySGI()
db = Database()


@app.route('/')
def index():
    return 'Hello world!'

if __name__ == '__main__':
    import os

    port = os.environ.get('PORT')
    app.run(port=port)
