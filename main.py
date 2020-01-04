
import sys
from a0_learner import A0Learner
from re_parser import REParser

if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
    print("""

    A0LREe - Learns Automaton from examples and extracts Regular Expression
    
    The pipeline consists of these stages:
        * Construct a Prefix Tree from the set of examples,
        * Convert Prefix Tree into Zero-Reversible Automaton,
        * State-Elimination Algorithm to extract Regex from Automaton,
        * Nested Regexes to simplify final pattern (work in progress).

    Requirements:
        Python packages for drawing graphs:
        * PyQt5
        * graphviz

    Arguments:
        -h              print this message
        -v              draw graphs and print debugging info
        filepath        expected as last argument, file with list of examples:
                            - each line should contain one example,
                            - empty line means empty string is accepted,
                            - no seperator symbols.

    Example:
        main.py -v example.txt
    """)
    sys.exit(0)

verbose = True if '-v' in sys.argv else False

# Try to open file with examples
fp = sys.argv[-1]
if fp[0] == '-':
    print('Missing argument: filepath. Exiting')
    sys.exit(0)
try:
    S = open(fp).read().split()
except (OSError) as ex:
    print(ex)
    print('Unable to read file [{}]. Exiting.'.format(fp))
    sys.exit(1)

# Stage 1, contruct prefix tree and 0-reversible automaton

L = A0Learner(S)
if verbose:
    print('Constructing 0-reversible automaton from examples.')
L.learn(verbose)
A = L.get_automaton()

# Stage 2, parse regular expressoin from automaton
P = REParser(A)
if verbose:
    print('Extracting regular expression from automaton.')
e = P.parse(verbose)
print('Final Expression: [{}]'.format('|'.join(e)))