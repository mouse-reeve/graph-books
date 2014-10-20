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
    node = graph.getNodeById(nodeId)

    return json.dumps(buildNodeJson(node))

@app.route('/api/node/<nodeId>', methods = ['PUT'])
def editNode(nodeId):
    data = request.get_json()
    node = graph.getNodeById(nodeId)
    node = graph.updateNode(data)

    # this isn't RESTful
    return json.dumps(buildNodeJson(node))

@app.route('/api/name-lookup/<name>', methods = ['GET'])
def findNodesByName(name):
    nodes = graph.getNodesByName(name)
    data = []
    for node in nodes:
        data.append(buildNodeJson(node[0]))
    return json.dumps(data)

@app.route('/api/node/relationships', methods = ['POST'])
def createRelationship():
    data = request.get_json()
    success = graph.createRelationship(data['start'], data['relationship'], data['end'])
    return getNode(data['start'])

def buildNodeJson(node):
    data = {
        'id': node.id,
        'properties': node.properties,
        'label': node.labels._labels.pop()._label,
        'relationships': {}
    }

    for relationship in node.relationships:
        if not relationship.type in data['relationships']:
            data['relationships'][relationship.type] = []
        data['relationships'][relationship.type].append({
            'properties': relationship.properties,
            'end': {
                'properties': relationship.end.properties,
                'label': relationship.end.labels._labels.pop()._label,
                'id': relationship.end.id
            },
            'start': {
                'properties': relationship.start.properties,
                'label': relationship.start.labels._labels.pop()._label,
                'id': relationship.start.id
            }
        })

    return data


if __name__ == '__main__':
    app.debug = True
    app.run(port=4000)
