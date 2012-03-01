## Implementation of the FP-Growth algorithm 

This project contains a python implementation of the FP-Growth algorithm
used for mining frequent itemsets. 

**Usage:**

    $ python fpgrowth.py -o output_file -s support -t treshold

Default values are:

output_file = fpgrowth-results.out

support = 3

treshold = 0.20

Input data must follow the schema:

Transaction ID[TAB]Timestamp[TAB]Item[TAB]Item count

for help use -h or --help
for verbose use -v or --verbose

