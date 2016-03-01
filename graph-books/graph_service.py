''' neo4j logic '''
import logging
import os

from py2neo import authenticate, Graph
from py2neo.error import Unauthorized
from py2neo.packages.httpstream.http import SocketError

class GraphService(object):
    ''' manage neo4j data operations '''

    def __init__(self):
        try:
            user = os.environ['NEO4J_USER']
            password = os.environ['NEO4J_PASS']
        except KeyError:
            logging.error('Environment variables for database authentication unavailable')
        else:
            authenticate('localhost:7474', user, password)

        try:
            graph = Graph()
            self.query = graph.cypher.execute
        except SocketError:
            logging.error('neo4j failed to load')
            self.query = lambda x: {}
        except Unauthorized:
            self.query = lambda x: {}

    def relate_nodes(self, node1_id, node2_id, rel_name):
        ''' create a relationship between two nodes '''
        self.query('MATCH n, m WHERE id(n) = %s AND id(m) = %s CREATE (n)-[:%s]->(m)' %
                   (node1_id, node2_id, rel_name))

    def add_node(self, label, params):
        ''' insert data '''
        node = self.query('CREATE (n:%s {params}) return n' % label, params=params)
        return node[0][0]

    def find_or_add_node(self, label, params):
        ''' insert data '''
        value = params['value'].replace('"', '\\"')
        find = self.query('MATCH (n:%s) WHERE n.value="%s" RETURN n' % (label, value))
        try:
            return find[0][0]
        except IndexError:
            node = self.query('CREATE (n:%s {params}) return n' % label, params=params)
            return node[0][0]
