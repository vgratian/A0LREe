
from nested_re import NestedRE

class REParser():

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
        self.verbose = False


    def parse(self, verbose=False):
        """
        Apply State-Elimination to extract regular expression from the automaton.

        :args:
            verbose     - print a lot of info (useful for debugging)
        :returns:
            regex       - string
        """

        self.verbose = verbose

        # Requirement of the SE algorithm, automaton should be uniform
        if not self.is_uniform():
            print('Converting to uniform Automaton')
            self.make_uniform()
            if verbose:
                self.A.show('Uniform 0-Automaton')
        
        # List nodes to be eliminated, ignore initial and final states
        nodes = [n for n in self.A.nodes if not (n.is_initial or n.is_final) ]

        i = 0
        while nodes:    
            # Choose node to be eliminated
            k = nodes.pop(0)
            new_edges = [ [ [] for i in range(self.A.esize)] for j in range(self.A.esize)]
  
            # DEBUG
            i+=1
            if verbose:
                print(f'Loop={i}, N={len(nodes)}, Eliminatin k={k}')
                self.A.show(f'i={i}')

            for n1 in list(self.A.nodes):
                for n2 in list(self.A.nodes):
                    if not (n1==k or n2==k):
                        new_label = self.derive_pattern(n1, n2, k)
                        if new_label:
                            new_edges[n1.index][n2.index].append( new_label )

            self.A.delete_node(k)
            self.A.edges = new_edges


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


    def derive_pattern(self, s, t, k):

        s2t = NestedRE( '|'.join(self.A.edges[s.index][t.index]) )
        s2k = NestedRE( '|'.join(self.A.edges[s.index][k.index]) )
        k2k = NestedRE( '|'.join(self.A.edges[k.index][k.index]), '*' )
        k2t = NestedRE( '|'.join(self.A.edges[k.index][t.index]) )

        if self.verbose:
            print('-' * 40)
            print(f'Deriving pattern for pair: [s={s.index}, t={t.index}, k={k.index}]')
            print('s2t; ', s2t)
            print('s2k; ', s2k)
            print('k2k; ', k2k)
            print('k2t; ', k2t)
        
        # Left-hand side of the pattern, which is just s2t or None if it's empty
        L = s2t if s2t else None

        # Right-hand side of the pattern, take the intersection of the three patterns
        R = None
        if s2k and k2t:
            #if s2k and s2k != ['ϵ']:
            #    right_pattern.append(s2k)
            R = s2k
            if self.verbose:
                print('[R = s2k]: ', str(R))

            if k2k and str(k2k) != 'ϵ':
                R = R.join_intersection(k2k)
                if self.verbose:
                    print('[R += k2k]: ', str(R))

            R = R.join_intersection(k2t)
            if self.verbose:
                print('[R += k2t]: ', str(R))

        # Full pattern, union of L and R
        P = None
        if L and R:
            P = L.join_union(R)
        elif L and not R:
            P = L
        elif R and not L:
            P = R

        if self.verbose:
            print('[P=L|R]: ', P)
            
        return str(P) if P else None


    def get_automaton(self):
        return self.A
