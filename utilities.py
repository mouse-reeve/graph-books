from neo4jrestclient.client import GraphDatabase, Node


class Utilities:

    def __init__(self):
        self.suppress_output = False

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def create_node(self, name, content_type, graph_name):
        if not self.suppress_output:
            print 'creating node %s, type %s, in %s' % \
                  (name, content_type, graph_name)
        node = self.gdb.node(name=name, contentType=content_type)
        node.labels.add(graph_name)
        return node

    def find_or_create_node(self, name, content_type, graph_name):
        name = name.replace('"', '')
        node = self.find_by_name(name, content_type, graph_name)
        if not node:
            node = self.create_node(name, content_type, graph_name)
        return node

    def find_by_name(self, name, contentType, graphName):
        q = 'MATCH (n:%s) WHERE n.contentType = "%s" ' \
            'AND n.name = "%s" RETURN n' % (graphName, contentType, name)
        nodes = self.gdb.query(q, returns=Node)
        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        return False

    def find_by_isbn(self, isbn, graph_name):
        q = 'MATCH (n:%s) WHERE n.isbn = "%s" RETURN n' % (graph_name, isbn)
        nodes = self.gdb.query(q, returns=Node)

        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        else:
            # checks for alternate ISBN format used by LibraryThing
            variant = isbn[0:-1]
            q = 'MATCH (n:%s) WHERE n.isbn =~ ".*%s.*" RETURN n' % \
                (graph_name, variant)
            nodes = self.gdb.query(q, returns=Node)
            if len(nodes) > 0 and len(nodes[0]) > 0:
                return nodes[0][0]
        return False

    def find_by_title(self, title, graph_name):
        q = 'MATCH (b:%s) WHERE b.name =~ "(?i).*%s.*" RETURN b' % \
            (graph_name, title)
        nodes = self.gdb.query(q, returns=Node)
        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        return False
