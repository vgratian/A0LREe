
**A0LREe**: 0-reversible Automaton * (**A<sub>0</sub>**) **L**earner and **R**egular **E**xpression **e**xtractor. Input of the program is a list of strings, output is a regular expression.


## Workflow ##

**A0LREe** is a pipeline of three algorithms:

- 0-Reversible Learner: constructs a Finite-State Automaton (FSA) from the list of strings
- State-Elimination: extracts a regular expression from the FSA
- Nested Regular Expressions (work in progress): simplifies the regular expression during the extraction process.

For a detailed description of these algorithms see the accompanying [paper](paper.pdf). For an example, see below.

## Requirements ##

- Python 3

The following Python packages a required for drawing graphs:
- graphviz
- PyQt5

both can be installed with pip.

## Usage ##

Mandatory argument:
* `<filepath>` (expected as **last** argument): path to file with list of strings, this should be:
  * each string on a seperate path
  * no seperator symbols
  * empty line means empty string should be accepted by the regular expression

Optional arguments:
* `-h`, `--help`: print help
* `-v`: draw graphs and print more info to STDOUT

Example:
```sh
$ python main.py -v examples.txt
```


## Example ##

The file `example.txt` contains the strings `[b, ab, aab, aaaab]`. A0LREe does its work in the following steps.

- Constructs a Prefix Tree, which is an FSA which accepts exactly these four strings
![alt text](/graphs/graph_01.png "Graph 1")


- Merges the accepting nodes of the Prefix Tree
![alt text](/graphs/graph_02.png "Graph 2")


- Merges nodes with non-deterministic transitions. The resulting graph is a 0-reversible FSA (see paper for the definition):
![alt text](/graphs/graph_03.png "Graph 3")

 
- The FSA is converted into a uniform FSA, which is required by the State-Elimination algorithm (SEA)
![alt text](/graphs/graph_04.png "Graph 4")


- SEA eliminates nodes of the FSA, until only an initial and a final nodes are left
![alt text](/graphs/graph_05.png "Graph 5")


- The resulting graph has only one edge, and the label of this edge is the output of the program.
![alt text](/graphs/graph_06.png "Graph 6")