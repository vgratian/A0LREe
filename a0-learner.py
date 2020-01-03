
from automaton import Automaton, Node

class A0Learner:
    """
    The algorithm is based on the Zero-Reversibe Inference Algorithm introduced
    by Dana Angluin (see Angluin, 1982).

    First from the set of examples a prefix tree is constructed (which is an 
    automaton that exactly accepts those examples). Then the prefix tree is 
    converted into a zero-reversible automaton by continuously merging states
    with identical incoming or outgoing edges, i.e. edges with the same label
    to the same target or source node.

    To do the learning, initialize an object and call the method learn().

    """

    def __init__(self, examples=None, automaton=None):
        """
        :args:
            automaton   - (optional) instance of Automaton class
            examples    - list of strings, this can include the empty string ('')
        """
        self.A = automaton if automaton else Automaton()
        self.S = sorted( set(examples) )
        self.Σ = {char for s in self.S for char in s}
        self.root = self.A.add_node(
                is_initial=True, 
                is_final=True if self.S[0] == '' else False 
                )
        # Drop empty string from list of examples
        if self.S[0] == '':
            self.S = self.S[1:]
        self.verbose = False


    def learn(self, verbose=True):
        """
        Constructs zero-reversible automaton in three stages:
        - Create prefix tree from examples
        - Merges all final states
        - Merges all nodes with identical edges.

        :args:
            verbose     - draw all intermediate graphs
        """

        self.verbose = verbose

        # Create prefix tree
        self.construct_prefix_tree()
        if verbose:
            self.A.show(title='Prefix Tree')

        # Merge final states
        self.merge_final_states()
        if verbose:
            self.A.show(title='Prefix Tree after merging final states')

        # Merge non-deterministic transitions
        self.merge_nd_edges()
        if verbose:
            self.A.show(title='Automaton with merged transitions')


    def construct_prefix_tree(self):
        """
        Create a prefix tree that exactly matches with the list of examples.
        To avoid creating duplicate paths (i.e. node-edge sequences with the same labels),
        we keep track of the previous path and add new labels for the next strings
        only continuing from the longest matching point.
        """

        if self.verbose:
            print(f'Constructing Prefix tree from S={self.S}')

        # List of label-node tuples, used to keep track the previous path.
        # (This guarantees we will not create duplicate paths, since the list of
        # examples is alphabetically sorted!)
        prefix_path = []

        for s in self.S:
            # First, find the longest match with the previous prefix path, to continue from there
            i=0
            for i in range( min( len(s), len(prefix_path) ) ):
                if s[i] != prefix_path[i][0]:
                   break
            prefix_path = prefix_path[:i]

            # Continue from the last matching point
            # Add new nodes to the last node in the prefix path
            for i in range( len(prefix_path), len(s) ):
                prev_node = prefix_path[-1][1] if prefix_path else self.root
                # Add last character in s as an accepting state
                new_node = self.A.add_node( is_final=True if i+1==len(s) else False )
                self.A.add_edge( prev_node, new_node, s[i])
                prefix_path.append( (s[i], new_node) )


    def merge_final_states(self):
        if self.verbose:
            print(f'Merging {len(self.A.accepting_nodes)} final states into one.')
        self.A.merge_nodes( list(self.A.accepting_nodes) )



    def merge_nd_edges(self):
        """
        Merge all non-deterministic (nd-) transitions in the automaton.
        Nd-transition are defined as: for any node n0, if it has outgoing 
        (respectively incoming) transitions with the same label to (from) a 
        set of nodes n1, n2 ... nk such that k>1, then those are nd.

        Find nd-edges in the automaton and merge the associated nodes. Repeat
        same process as long as there were nd-transitions found during
        last iteration.
        """

        # Merge outgoing nd-transitions
        still_nd = True
        while still_nd:
            if self.verbose:
                print('Finding and merging outgoing nd-edges.')
            still_nd = False
            for n in list(self.A.nodes):
                if n.index in self.A.deleted_indices:
                    continue
                for char in self.Σ:
                    nd_children = []
                    for c in list(self.A.nodes):
                        if c.index in self.A.deleted_indices or c.index == n.index:
                            continue
                        if char in self.A.edges[c.index][n.index]:
                            nd_children.append(c)
                    if len(nd_children) > 1:
                        self.A.merge_nodes(nd_children)
                        still_nd = True

        # Merge incoming nd-transitions
        still_nd = True
        while still_nd:
            if self.verbose:
                print('Finding and merging incoming nd-edges.')
            still_nd = False
            for n in list(self.A.nodes):
                if n.index in self.A.deleted_indices:
                    continue
                for char in self.Σ:
                    nd_parents = []
                    for p in list(self.A.nodes):
                        if p.index in self.A.deleted_indices or p.index == n.index:
                            continue
                        if char in self.A.edges[p.index][n.index]:
                            nd_parents.append(p)
                    if len(nd_parents) > 1:
                        self.A.merge_nodes(nd_parents)
                        still_nd = True


    def get_automaton(self):
        return self.A


if __name__ == '__main__':
    S = ['', 'ab', 'aab', 'aaaab']
    A = Automaton()
    L = A0Learner(S, A)
    L.learn(verbose=True)
