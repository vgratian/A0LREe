

class RegExParser():

    """
    Extract a regular expression from a 0-reversible automaton. This is an
    implementation of the State-Elimination Algorithm (as described in  Getir,
    e.a. 2007).

    On each iteration a node is eliminated and its edges are merged to the other
    nodes in the Automaton. At the end we have only an initial and a final node,
    and the label of their edge is the regular expression.

    This is work in progress and I am still looking for a away to simplify the
    final expression (hence for the moment this is only an extractor and not
    a parser).
    

    """

    def __init__(self, automaton):
        """
        :args:
            automaton   - an deterministic FSA, instance of Automaton
        """

        self.A = automaton


    def parse_re(self, verbose=False):
        """
        Apply State-Elimination to extract regular expression from the automaton.

        :args:
            verbose     - print a lot of info (useful for debugging)
        :returns:
            regex       - string
        """


        # Requirement of the SE algorithm, automaton should be uniform
        if not self.is_uniform():
            print('Converting Automaton to uniform FSA')
            self.make_uniform()

        # List nodes to be eliminated, ignore initial and final states
        nodes = [n for n in self.A.nodes if not (n.is_initial or n.is_final) ]

        final_edge = None

        while nodes:          
            # Choose node to be eliminated
            k = nodes.pop(0)
            new_edges = [ [ [] for i in range(self.A.esize)] for j in range(self.A.esize)]

            print('Eliminating: ', k)

            for n1 in list(self.A.nodes):
                for n2 in list(self.A.nodes):
                    if not (n1==k or n2==k):
                        new_label = self.merge_patterns(n1, n2, k)
                        if new_label:
                            new_edges[n1.index][n2.index].append( new_label )

            self.A.edges = new_edges

            if verbose:
                self.A.show(title=f'RegExParser: eliminated {i} state(s)')

            
        final_edge = self.A.edges[self.A.root.index][self.A.accepting_nodes[0].index]
        
        return final_edge


    def is_uniform(self):
        """
        Check if automaton is uniform, i.e.
        - has exactly one initial state with no incoming edges
        - has exactly one final states with no outgoing edges
        """

        # Class Automaton only allows one initial state, so only check incoming edges
        if any(e[self.A.root.index] for e in self.A.edges):
            return False

        # There should be only one final state
        if len(self.A.accepting_nodes) > 1:
            return False

        # Final state should not have outgoing edges
        f = self.A.accepting_nodes[0]
        if any( self.A.edges[f.index] ):
            return False

        return True


    def make_uniform(self):
        """
        Convert automaton to a uniform automaton. This is done by adding a new
        initial state with a ϵ-transition to the previous initial state.
        Similarly, we create a new final state and add a ϵ-transition from the
        previous final state(s).
        """

        # If inital state is final state or if inital state has incoming edges
        # create new initial state with ϵ-transition the old one
        if self.A.root in self.A.accepting_nodes or any(e[self.A.root.index] for e in self.A.edges):
            new_root = self.A.add_node()
            self.A.add_edge(new_root, self.A.root, 'ϵ')
            self.A.root.is_initial = False
            new_root.is_initial = True
            self.A.root = new_root

        # If there are more than one final states or a final state has outgoing edges
        # create new final state with ϵ-transition(s) to the old final state(s)
        if len(self.A.accepting_nodes) > 1 or any(self.A.edges[self.A.accepting_nodes[0].index]):
            new_final = self.A.add_node()
            for f in self.A.accepting_nodes:
                self.A.add_edge(f, new_final, 'ϵ')
                f.is_final = False
            new_final.is_final = True
            self.A.accepting_nodes = [ new_final ]


    def merge_patterns(self, s, t, k):


        s2t = ''.join(self.A.edges[s.index][t.index])
        s2k = ''.join(self.A.edges[s.index][k.index])
        k2k = ''.join(self.A.edges[k.index][k.index])
        k2t = ''.join(self.A.edges[k.index][t.index])

        right_pattern = ''
        if s2k and k2t:
            if s2k and s2k != 'ϵ':
                right_pattern += s2k 

            if k2k and k2k != 'ϵ':
                if len(k2k) == 1:
                    right_pattern += k2k + '*'
                else:
                    right_pattern += '(' + k2k + ')*'

            if k2t and k2t != 'ϵ':
                right_pattern += k2t

            # Temporary fix if both s2k and k2t are 'ϵ'
            if not right_pattern and not s2t and s2k=='ϵ' and k2t == 'ϵ':
                right_pattern = 'ϵ'

        if s2t and right_pattern:
            return '(' + s2t + '|' + right_pattern + ')'
        elif s2t and not right_pattern:
            return s2t
        elif right_pattern and not s2t:
            return right_pattern
        return None


    def get_automaton(self):
        return self.A
