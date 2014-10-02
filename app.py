from flask import Flask, request, make_response, g

# CONFIG
DEBUG = True
app = Flask(__name__)

@app.route('/')
def index():
    return make_response(open('index.html').read())

if __name__ == '__main__':
    app.debug = True
    app.run(port=4000)
