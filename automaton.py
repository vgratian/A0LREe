import sys
import time
from graphviz import Digraph
from PyQt5 import QtGui, QtWidgets


class Automaton:
    """
    A Finite State Automaton (FSA), a di-graph with the following elements:
        - nodes (or states): can be initial or accepting or neither
        - edges: transitions between nodes or a self-loop edge.
        - each edge has a label from some finite alphabet

    Edges are represented by a matrix (list of lists), where each label is a list
    itself (each element is an transition rule).

    We rely on graphviz and Qt to draw an image of the FSA.

    """
    def __init__(self):
        self.nodes = []
        self.node_index = 0
        self.root = None
        self.accepting_nodes = []
        self.deleted_indices = set()
        self.esize = 100
        self.edges = [ [ [] for i in range(self.esize)] for j in range(self.esize)]
        self.graph_fp = 'graphs/dfs_' + str(round(time.time()))
        self.graph = Digraph('finite_state_machine', format='png', filename=self.graph_fp)
        self.graph.attr(rankdir='LR', size='10')        


    def __str__(self):
        return ' Root: [{}]\n Nodes [{}]: ({})\n Final [{}]: [{}]\n Edges [{}]: [{}]'.format(
            self.root.label if self.root else 'None',
            len(self.nodes),
            ', '.join(n.label for n in self.nodes),
            len(self.final_states),
            ', '.join(n.label for n in self.final_states),
            len(self.edges),
            ', '.join('({}=>{}, "{}")'.format(e.source.name, e.target.name, e.label) for e in self.edges)
                )


    def add_node(self, is_initial=False, is_final=False, label=''):
        """
        Creates a node object and make sure that the matrix self.edges is larger
        than the number of nodes.
        """
        if len(self.nodes) > self.esize:
            self.expand_edges()

        node = Node( self.node_index, label, is_initial, is_final)
        self.node_index += 1
        self.nodes.append( node )

        if not self.root or is_initial:
            self.root = node
        if is_final:
            self.accepting_nodes.append( node )
        return node


    def delete_node(self, node):
        """
        Remove node from lists and keep track of its index
        (this is necessary to ignore edges of deletd nodes later).
        """
        self.deleted_indices.add( node.index )
        self.nodes.remove(node)
        if node in self.accepting_nodes:
            self.accepting_nodes.remove(node)


    def merge_nodes(self, nodes, new_label=''):
        """
        Merges a list of nodes into a new node.
        All edges to and from the merged nodes are reassigned to the new node.

        :args:
            nodes       - list of Node objects
            new_label   - string, label of the new node
        :returns:
            new_node    - Node object
        """

        # Keep track track of the indices of the nodes to be merged, so we 
        # don't try to merge the new node as well (e.g. when it's accepting node)
        merge_indices = [n.index for n in nodes]
        #print(f'preparing to merge nodes: {merge_indices}') 

        # Create new Node object
        # If any of the old nodes is initial or accepting, inherit this property
        new_node = self.add_node(
                        is_initial=True if any([n.is_initial for n in nodes]) else False, 
                        is_final=True if any([n.is_final for n in nodes]) else False,
                        label=new_label
                        )
        new_i = new_node.index
        #print(f'created new node with index {new_i}')
        # Merge edges from nodes and delete
        for n1 in list(self.nodes):
            for n2 in list(self.nodes):
                if self.edges[n1.index][n2.index] and (n1.index in merge_indices or n2.index in merge_indices):
                    # Edge is selfloop or edge is between nodes to be merged
                    if n1.index == n2.index or (n1.index in merge_indices and n2.index in merge_indices):
                        #print('<=>', self.edges[n1.index][n2.index])
                        self.add_edges(new_node, new_node, self.edges[n1.index][n2.index])
                    # Edge is *from* nodes to be merged
                    elif n1.index in merge_indices:
                        #print('<=', self.edges[n1.index][n2.index])
                        self.add_edges(new_node, n2, self.edges[n1.index][n2.index])
                    # Edge is *to* nodes to be merged
                    elif n2.index in merge_indices:
                        #print('=>', self.edges[n1.index][n2.index])
                        self.add_edges(n1, new_node, self.edges[n1.index][n2.index])
                    # Delete old edge
                    self.edges[n1.index][n2.index] = []

        # Delete merged nodes
        for node in list(nodes):
            self.delete_node(node)
        # Update initial and final states
        if new_node.is_initial:
            self.root = new_node
        if new_node.is_final:
            self.accepting_nodes = [new_node]

        return new_node


    def add_edge(self, n1, n2, label):
        self.edges[n1.index][n2.index].append(label)


    def add_edges(self, n1, n2, labels):
        if not self.edges[n1.index][n2.index]:
            self.edges[n1.index][n2.index] = labels
        else:
            for label in labels:
                if label not in self.edges[n1.index][n2.index]:
                    self.edges[n1.index][n2.index].append(label)


    def get_edge(self, n1, n2):
        edge = self.edges[n1.index][n2.index]
        return edge if edge != [''] else None


    def delete_edge(self, n1, n2):
        self.edges[n1.index, n2.index] = ['']


    def expand_edges(self):
        """
        Replaces the current edges matrix with one twice as large.
        """
        #print(f'Expanding E matrix from {self.esize} to {self.esize*2}')
        self.esize *= 2
        new_edges = [[self.edges[i][j] if i <= self.node_index and j <= self.node_index else [] \
            for i in range(self.esize)] for j in range(self.esize)]
        self.edges = new_edges


    def show(self, title='Finite State Automaton'):
        """
        Open a QT window and draw Automaton with graphviz.
        """
        self.reset_graph()
        self.graph.render()
        App = QtWidgets.QApplication(sys.argv)
        W = QtWidgets.QWidget()
        L = QtWidgets.QLabel(W)
        L.setText("Your Finite State Automaton:")
        P = QtGui.QPixmap(self.graph_fp + '.png')
        L.setPixmap(P)
        W.setGeometry(0, 0, P.width()+100, P.height()+50)
        L.move(50,20)
        W.setWindowTitle(title)
        W.show()
        App.exec_()        


    def reset_graph(self):
        """
        Reconstruct a new graphviz graph
        """
        self.graph.clear()
        # Add all nodes
        for node in self.nodes:
            if node == self.root or node.is_initial:
                self.graph.attr('node', 
                                width='0.8', 
                                height='0.8', 
                                shape='circle', 
                                style='filled', 
                                fillcolor='yellow' )
            if node.is_final:
                self.graph.attr( 'node', 
                                shape='doublecircle', 
                                style='filled', 
                                fillcolor='lightskyblue' )
            else:
                self.graph.attr( 'node', 
                                shape='circle', 
                                style='filled', 
                                fillcolor='azure2' )
            label = '<q<SUB><FONT POINT-SIZE="10">' + str(node.index) + '</FONT></SUB>>'
            self.graph.node( str(node.index), label=label )
        # Add edges
        for i in range(self.node_index+1):
            if i not in self.deleted_indices:
                for j in range(self.node_index+1):
                    if self.edges[i][j] and j not in self.deleted_indices:
                        self.graph.edge(str(i), str(j), label=''.join(self.edges[i][j]))



class Node:
    def __init__(self, index,  label='', is_initial=False, is_final=False):
        self.index = index
        self.label = label
        self.is_initial = is_initial
        self.is_final = is_final

    def __str__(self):
        return f'NODE: ("{self.index}"), Initial: {self.is_initial} Final: {self.is_final}'

