from flask import Flask, request, make_response, g
from graphService import GraphService

import json

# CONFIG
DEBUG = True
app = Flask(__name__)

graph = GraphService()

@app.route('/', defaults={'path': None})
@app.route('/<path:path>')
def index(path):
    return make_response(open('index.html').read())

@app.route('/api/node/<nodeId>', methods = ['GET'])
def getNode(nodeId):
    data = graph.getNodeById(nodeId)
    if not data:
        return json.dumps({'success': False})

    return json.dumps(data)

@app.route('/api/name-lookup/<name>', methods = ['GET'])
def findNodeByName(name):
    data = graph.getNodeByName(name)
    return json.dumps(data)

if __name__ == '__main__':
    app.debug = True
    app.run(port=4000)
