
class NestedRE():
    """
    Nested Regular expression. The goal is to simplify Regex patterns by
    taking the intersection or unton of nested expressions and merging it
    with other NestedRE instances.

    TODO: This is work in progress, not completed yet. Only very basic 
    merge / join is possible for now.

    :args:
        exp     - ether string or a (nested) list of RE instances
        closure - one of: '*', '+', '?' or '' if none.

    """

    def __init__(self, exp, closure=''):

        assert type(exp) is str or type(exp) is list, 'Expected string or list.'

        self.exp = exp
        self.closure = closure


    def __bool__(self):
        """
        Check wether expression is empty.
        """
        return bool(self.exp)


    def __str__(self):
        """
        Convert expression into "flat" string, i.e. merge nested expressions.
        """
        return self.make_flat()


    def is_flat(self):
        return True if type(self.exp) == str else False


    def make_flat(self):
        """
        If we have simple expression, return just the concatenation of the 
        expression and closure. If we have nested expressions, recursively
        make them flat and concatenate.
        """

        if type(self.exp) == str:
            if not self.closure or self.exp == 'ϵ':
                return self.exp
            elif len(self.exp) == 1:
                return self.exp + self.closure
            else:
                return '(' + self.exp + ')' + self.closure
        else:
            flat_exp = ''.join( str(e) for e in self.exp )
            if not self.closure or flat_exp == 'ϵ':
                return flat_exp
            elif len(flat_exp) == 1:
                return flat_exp + self.closure
            else:
                return '(' + flat_exp  + ')' + self.closure


    def join_intersection(self, other):
        """
        Joins the patterns of self and other by intersection.
        If the patterns are the same, we merge them. Otherwise
        just concatenate. 
        
        TODO: merge complex and nested patterns

        :args:
            other - NestedRE instance

        :returns:
            X     - NestedRE with merged patterns
        """

        assert type(self) is type(other), 'Expected NestedRE instance'

        A = self.make_flat()
        B = other.make_flat()

        #print('JI, A=', A, 'B=', B)

        if A == B and A !='ϵ':
            return self.merge_by_intersection(A, [self.closure, other.closure])
        elif A == 'ϵ' and B == 'ϵ':
            return NestedRE('ϵ')
        elif A == 'ϵ':
            return other
        elif B == 'ϵ':
            return self
        else:
            return NestedRE(A+B)


    def merge_by_intersection(self, p, C):
        """
        Merge identical pattern with possibly different closures into one. 
        Merge by intersection, i.e. by the following rules:
       
            p ^ p = pp
            p ^ p? = pp?
            p? ^ p? = a?a?
            p ^ p+ = pp+
            p ^ p* = p+
            p? ^ p+ = p+
            p+ ^ p* = p+
            p+ ^ p+ = p+
            p? ^ p* = p*
            p* ^ p* = p*
        
        :args:
            p       - string: pattern
            C       - list of two elements, the closures of the two instances,
                      should be one of:  '*', '+', '?' or '' if none.
        :returns:
            X       - NestedRE instance with merged pattern.
        """
 
        if '' in C:
            # At least one of two without clusure
            if '?' in C:
                return NestedRE(p+p, '?')
            elif '*' in C:
                return NestedRE(p, '+')
            elif '+' in C:
                return NestedRE(p+p, '+')
            else:
                # Both without closure
                return NestedRE(p+p)
        # At least one has "+"
        elif '+' in C:
            return NestedRE(p, '+')
        elif '*' in C:
            return NestedRE(p, '*')
        # Only option left: both "?"
        else:
            return NestedRE(p+'?'+p+'?')
            

    def join_union(self, other):
        """
        Joins the patterns of self and other by union.
        If the patterns are the same, simply return one. Otherwise
        concatenate with '|'. 
        
        TODO: merge complex and nested patterns

        :args:
            other - NestedRE instance

        :returns:
            X     - NestedRE with merged patterns
        """

        assert type(self) is type(other), 'Expected NestedRE instance'

        A = self.make_flat()
        B = other.make_flat()

        if A == B and A !='ϵ':
            return self.merge_union(A, [self.closure, other.closure])
        elif A == 'ϵ' and B == 'ϵ':
            return NestedRE('ϵ')
        elif A == 'ϵ':
            return NestedRE(B, '?')
        elif B == 'ϵ':
            return NestedRE(A, '?')
        else:
            return NestedRE( '(' + A + '|' + B + ')' )


    def merge_by_union(self, p, C):
        """
        Merge identical pattern with possibly different closures into one. 
        Merge by union, i.e. by the following rules:

            a + a = a
            a + a? = a?
            a + a+ = a+
            a? + a+ = a*
            a + a* = a? + a* = a* + a* = a*

        :args:
            p       - string: pattern
            C       - list of two strings, the closures of the two instances,
                      should be one of:  '*', '+', '?' or '' if none.
        :returns:
            X       - NestedRE instance with merged pattern.            
        """

        assert len(A) == 2 and len(B) == 2, "[merge_disjunction] only simple re-s accepted"

        if '*' in C:
            # If any is *, then merged pattern is *
            return NestedRE(p, '*')
        elif '+' in C and '?' in C:
            # One is mandatory, other optional, so merged pattern is * again
            return NestedRE(p, '*')
        elif '+' in C:
            # One is mandatory, then merged pattern is mandatory
            return NestedRE(p, '+')
        elif '?' in C:
            # One is optional, so merged pattern is optional
            return NestedRE(p, '?')
        else:
            # Only option left: none has closure
            return NestedRE(p)