## Implementation of the FP-Growth algorithm for mining frequent itemsets

**Usage:**

    $ python fpgrowth.py -o output_file -s support -t treshold

Default values are:

    output_file = fpgrowth-results.out
    support = 3
    treshold = 0.20

Input data must follow the schema:
<Transaction ID>\t<Timestamp>\t<Item>\t<Item count>

for help use -h or --help
for verbose use -v or --verbose

**Input sample**

    100 0 f 1
    100 0 a 1
    100 0 c 1
    100 0 d 1
    100 0 g 1
    100 0 i 1
    100 0 m 1
    100 0 p 1
    200 0 a 1
    200 0 b 1
    200 0 c 1
    200 0 f 1
    200 0 l 1
    200 0 m 1
    200 0 o 1
    300 0 b 1
    300 0 f 1
    300 0 h 1
    300 0 j 1
    300 0 o 1
    400 0 b 1
    400 0 c 1
    400 0 k 1
    400 0 s 1
    400 0 p 1
    500 0 a 1
    500 0 f 1
    500 0 c 1
    500 0 e 1
    500 0 l 1
    500 0 p 1
    500 0 m 1
    500 0 n 1

**Results:**

Resulting frequent patterns:
c, f (count: 3)
a, c (count: 2)
a, c, f (count: 2)
a, f (count: 2)
a, m, f (count: 1)
c, m, f (count: 1)
m, f (count: 1)
a, m (count: 1)
c, m (count: 1)
p, c (count: 1)
