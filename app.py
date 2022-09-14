from pysgi import PySGI

app = PySGI()


@app.route('/')
def index():
    return 'Hello world!'

if __name__ == '__main__':
    import os

    port = os.environ.get('PORT')
    app.run(port=port)
