## Implementation of the FP-Growth algorithm 

This project contains a python implementation of the FP-Growth algorithm
used for mining frequent itemsets. See http://en.wikipedia.org/wiki/Association_rule_learning#cite_note-fp-growth-17
for more information.

**Usage:**

    $ python fpgrowth.py -o output_file -s support -t treshold

use -h or --help for help and -v or --verbose for verbose

**Default config:**

- output_file = fpgrowth-results.out
- support = 3
- treshold = 0.20

**Input data:**

Input data must follow the schema:

Transaction ID\<TAB\>Timestamp\<TAB\>Item\<TAB\>Item count

