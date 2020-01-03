import time
import sys
from graphviz import Digraph
from PyQt5 import QtGui, QtWidgets


class Automaton:
    """
    A Finite State Automaton (FSA), a di-graph with the following elements:
        - nodes (or states): can be initial or accepting or neither
        - edges: arcs between nodes or a self-loop arc.
        - each edge has a label

    Edges are represented by a matrix (list of lists), while each label is a list
    itself (each element is an edge).

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

        # Create new Node object
        # If any of the old nodes is initial or accepting, inherit this property
        new_node = self.add_node(
                        is_initial=True if any([n.is_initial for n in nodes]) else False, 
                        is_final=True if any([n.is_final for n in nodes]) else False,
                        label=new_label
                        )
        new_i = new_node.index
        merge_indices = [n.index for n in nodes]
        # Merge edges from nodes and delete
        for i in range(self.node_index+1):
            for j in range(self.node_index+1):
                if self.edges[i][j] and (i in merge_indices or j in merge_indices):
                    # Edge is selfloop or edge is between nodes to be merged
                    if i == j or (i in merge_indices and j in merge_indices):
                        self.add_edges(new_node, new_node, self.edges[i][j])
                    # Edge is *from* nodes to be merged
                    elif i in merge_indices:
                        self.add_edges(new_node, self.nodes[j], self.edges[i][j])
                    # Edge is *to* nodes to be merged
                    elif j in merge_indices:
                        self.add_edges(self.nodes[i], new_node, self.edges[i][j])
                    # Delete old edge
                    self.edges[i][j] = []

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
        print(f'Expanding E matrix from {self.esize} to {self.esize*2}')
        self.esize *= 2
        new_edges = [[self.edges[i][j] if i <= self.node_index and j <= self.node_index else [] \
            for i in range(self.esize)] for j in range(self.esize)]
        self.edges = new_edges


    def merge_outgoing_nd_edges(self):
        is_non_deterministic = True
        while is_non_deterministic:
            print('Merging non-detreministic OUTGOING edges')
            all_are_nd = []
            for node in list(self.nodes):
                is_nd, targets = node.find_nd_outgoing()
                all_are_nd.append( is_nd )
                if is_nd:
                    print('ND NODE: ', node)
                    for label in targets:
                        if len(targets[label]) > 1:
                            print(' ={}: [{}]'.format(label, ', '.join(n.label for n in targets[label])))
                            self.merge_nodes( targets[label])
            is_non_deterministic = any(all_are_nd)


    def merge_incoming_nd_edges(self):
        is_non_deterministic = True
        while is_non_deterministic:
            print('Merging non-detreministic INCOMING edges')
            all_are_nd = []
            for node in list(self.nodes):
                nd, sources = node.find_nd_incoming()
                all_are_nd.append(nd)
                if nd:
                    print('ND NODE: ', node)
                    for label in sources:
                        if len(sources[label]) > 1:
                            print(' ={}: [{}]'.format(label, ', '.join(n.label for n in sources[label])))
                            self.merge_nodes( sources[label])
            is_non_deterministic = any(all_are_nd)

    def merge_final_states(self, new_label=''):
        self.merge_nodes( self.final_states() )



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
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def has_edge_from(self, source, label):
        for edge in self.edges:
            if edge.source is source and edge.label==label:
                return True
        return False

    def has_edge_to(self, target, label):
        for edge in self.edges:
            if edge.target is target and edge.label==label:
                return True
        return False

    def has_selfloop(self, label):
        for edge in self.edges:
            if edge.is_selfloop and edge.label == label:
                return True
        return False

    def find_nd_outgoing(self):
        """
        Finds all outgoing edges and sorts by edge label.
        If same label points to more than one neighbor, node is non-deterministic, 
        Returns: bool, dict
        """
        edges_by_label = {}     
        for edge in self.edges:
            if edge.source is self and not edge.is_selfloop:
                if edge.label not in edges_by_label:
                    edges_by_label[edge.label] = []
                edges_by_label[edge.label].append(edge.target)
        is_nd = any([True if len(targets)>1 else False for targets in edges_by_label.values()])
        return is_nd, edges_by_label


    def find_nd_incoming(self):
        edges_by_label = {}     
        for edge in self.edges:
            if edge.target is self and not edge.is_selfloop:
                if edge.label not in edges_by_label:
                    edges_by_label[edge.label] = []
                edges_by_label[edge.label].append(edge.source)
        is_nd = any([True if len(sources)>1 else False for sources in edges_by_label.values()])
        return is_nd, edges_by_label



    def __str__(self):
        return f'NODE: ("{self.name}"), S: {self.is_initial} F: {self.is_final} EDGES {len(self.edges)}'


class Edge:
    def __init__(self, n1, n2, label):
        self.label = label
        self.source = n1
        self.target = n2
        self.is_selfloop = True if n1 == n2 else False

        # Add self to nodes
        n1.add_edge(self)
        if n1 != n2:
            n2.add_edge(self)

    def __str__(self):
        return f'EDGE: ("{self.label}"), {self.source.name} ==> {self.target.name}'


if __name__ == '__main__':
    DFA = Automaton()
    n0 = DFA.add_node()
    n1 = DFA.add_node()
    n2 = DFA.add_node(is_final=True)
    n3 = DFA.add_node(is_final=True)
    DFA.add_edge( DFA.root, n1, '0')
    DFA.add_edge( n1, n2, '0')
    DFA.add_edge( n1, n3, '1')
    DFA.add_edge( n3, n3, '2')
    print('Generated prefix tree')
    DFA.show(title='Prefix Tree')
    DFA.merge_nodes([n2, n3])
    DFA.show()
    print('Merged n2 and n3')
    #DFA.merge_nodes(DFA.final_states, are_final=True)
    print('Merged final states')
   # DFA.show(title='Merged final states')