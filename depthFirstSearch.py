''' implementation of depth-frst serarch algo '''
from neo4jrestclient.client import GraphDatabase, Node

class DepthFirstSearch(object):
    ''' updates and modifies the book database '''

    def __init__(self):
        self.suppress_output = False
        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def depth_first_search(self, input_graph, output_graph):
        ''' begin search '''
        # select the start node from the tree
        q = 'MATCH (n:%s) RETURN n LIMIT 1' % input_graph
        node = self.gdb.query(q, returns=Node)[0][0]

        self.add_dfs_node(node, output_graph)

    def add_dfs_node(self, mst_node, output_graph, dfs_parent_node=None):
        ''' recursively traverse graph '''
        if not self.suppress_output:
            print mst_node.properties['name']

        # add the new node
        dfs_node = self.gdb.node(name=mst_node.properties['name'],
                                 isbn=mst_node.properties['isbn'])
        dfs_node.labels.add(output_graph)

        # connect it to its parent
        if dfs_parent_node:
            dfs_parent_node.Knows(dfs_node)

        # get the children
        q = 'MATCH n1 --> n2 WHERE id(n1) = %d ' \
            'RETURN n2 ORDER BY n2.weight DESC' % mst_node.id
        children = self.gdb.query(q, returns=Node)

        if len(children) > 0:
            # recursively call this method for each child
            for child in children:
                dfs_node = self.add_dfs_node(child[0], output_graph, dfs_node)

        return dfs_node
