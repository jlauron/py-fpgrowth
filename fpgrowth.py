#!/usr/bin/env python
# encoding: utf-8
"""
fpgrowth.py

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Created by Julien Lauron
"""

import sys
import sets
import getopt

HELP_MESSAGE = '''Implementation of the FP-Growth algorithm for mining frequent itemsets
--
Usage: $ python fpgrowth.py -o output_file -s support -t treshold
--
Default values are:
  output_file = "fpgrowth-results.out"
  support = 3
  treshold = 0.20

Verbose mode (-v|--verbose) will output the frequent pattern tree in dot format on stdout
'''

TID_COL = 0
TIME_COL = 1
ITEM_COL = 2
NUMBER_COL = 3

class FPTreeNode:
    def __init__(self, item):
        self.item = item
        self.count = 1
        self.sub_nodes = []
        self.next_node_link = None

class HeaderTableEntry:
    def __init__(self, item, frequency):
        self.item = item
        self.frequency = frequency
        self.first_node = None
        self.last_node = None

class FPGrowth:
    """ Class implementing the FPGrowth algorithm used for frequent itemsets
    mining. It builds the FPTree from given data source parser and mine the
    constructed tree to output most frequent itemsets """

    def __init__(self, support, treshold):
        self.support = support
        self.treshold = treshold
        # Table item - head of node-links - tail of node links
        self.header_table = {}

    def build_tree(self, data_parser):
        """ Build the FPTree from given data parser """
        # Hash table to count item frequencies on first pass
        frequency_counts = {}
        # Root node
        self.root_node = FPTreeNode(None)
        # First pass
        for line in data_parser.get_data():
            if line == "":
                break
            infos = line.split(" ")
            item = infos[ITEM_COL]
            if frequency_counts.has_key(item):
                frequency_counts[item] += 1
            else:
                frequency_counts[item] = 1
        # Keep only frequent items
        frequent_items = []
        for item in frequency_counts:
            if frequency_counts[item] >= self.support:
                frequent_items.append((item, frequency_counts[item]))
                self.header_table[item] = HeaderTableEntry(item, frequency_counts[item])
        frequency_counts.clear()
        frequent_items.sort(lambda a, b: cmp(b[1], a[1]))
        for i in xrange(len(frequent_items)):
            frequent_items[i] = frequent_items[i][0]

        # Tree Building
        data_parser.reinit()
        currentlines = []
        line = data_parser.get_data().next()
        if len(line) > 0:
            splitline = line.split(" ")
            if splitline[ITEM_COL] in frequent_items:
                currentlines.append(splitline)
            transaction = splitline[TID_COL]
            while len(line) > 0:
                # Get all items for a transaction
                line = data_parser.get_data().next()
                splitline = line.split(" ")
                while len(splitline) > 0 and splitline[TID_COL] == transaction:
                    if splitline[ITEM_COL] in frequent_items:
                        currentlines.append(splitline)
                    line = data_parser.get_data().next()
                    splitline = line.split(" ")
                # Sort items for a given transaction (by frequency)
                for i in xrange(len(currentlines)):
                    item = currentlines[i][ITEM_COL]
                    currentlines[i] = (currentlines[i], frequent_items.index(item))
                if len(currentlines) > 0:
                    currentlines.sort(lambda a, b: cmp(a[1], b[1]))
                    # Process items and update the FP-Tree
                    self.__update_tree(currentlines)
                    del currentlines[:]
                if len(line) > 0:
                    if splitline[ITEM_COL] in frequent_items:
                        currentlines.append(splitline)
                    transaction = splitline[TID_COL]

    def __update_tree(self, to_process):
        """ Update the FPTree with given data line list of tuples """
        current_node = self.root_node
        for data_line in to_process:
            item = data_line[0][ITEM_COL]
            create_node = True
            for sub_node in current_node.sub_nodes:
                if sub_node.item == item:
                    sub_node.count += 1
                    current_node = sub_node
                    create_node = False
                    break
            if create_node:
                new_node = FPTreeNode(item)
                current_node.sub_nodes.append(new_node)
                current_node = new_node
                if self.header_table[item].first_node is None:
                    self.header_table[item].first_node = new_node
                else:
                    self.header_table[item].last_node.next_node_link = new_node
                self.header_table[item].last_node = new_node

    def mine(self):
        """ Mine the FPTree
        outputs a dict where each key is the frequent pattern (itemset) and the value
        is the number of times it was seen in the dataset
        """
        header_list = []
        for item in self.header_table.itervalues():
            header_list.append(item)
        header_list.sort(lambda a, b: cmp(a.frequency, b.frequency))
        # For each item in the header table, build its conditionnal pattern base
        # and use it to output the frequent itemsets containing that item
        frequent_patterns = {}
        for entry in header_list:
            paths = self.__build_paths(entry.item)
            res = {}
            for path in paths:
                item_list = path[0]
                freq = path[1]
                for item in item_list:
                    if res.has_key(item):
                        res[item] += freq
                    else:
                        res[item] = freq
                del item_list
            del paths
            prefix_path = []
            for item in res:
                if res[item] >= self.support:
                    prefix_path.append((item, res[item]))
            # Build frequent patterns from prefix path
            res = self.__build_frequent_patterns(prefix_path, entry.item)
            for r in res:
                if frequent_patterns.has_key(r):
                    frequent_patterns[r] += 1
                else:
                    frequent_patterns[r] = 1

        return frequent_patterns

    def __build_frequent_patterns(self, prefix_path, item):
        """ Build all permutations of elements from the given prefix path
        and item """
        if len(prefix_path) == 0:
            return []

        frequent_patterns = []
        prefix_path.append((item, 0))
        for length in xrange(1, len(prefix_path)):
            if length > 0:
                i = 0
                while (i + length) <= len(prefix_path):
                    x = i + 1
                    while (x + length) <= len(prefix_path):
                        set = [prefix_path[i][0]]
                        z = x
                        while (z - x) < length:
                            set.append(prefix_path[z][0])
                            z += 1
                        set = sets.ImmutableSet(set)
                        frequent_patterns.append(set)
                        x += 1
                    i += 1

        return frequent_patterns

    def __build_paths(self, item):
        results = []

        for node in self.root_node.sub_nodes:
            res = self.__build_paths_rec(item, node)
            if res != None and len(res) > 0:
                results.extend(res)

        return results

    #TODO: make this part iterative instead of recursive, to avoid the maximum
    # number of recursion reached
    def __build_paths_rec(self, item, node):
        if node.item == item:
            return [([], node.count)]
        else:
            res = []
            for sub_node in node.sub_nodes:
                l = self.__build_paths_rec(item, sub_node)
                if l != None:
                    for paths in l:
                        paths[0].append(node.item)
                    res.extend(l)
            if len(res) == 0:
                return None
            else:
                return res

    def print_tree(self):
        """ Output the built FPTree in dot format """
        nodeid, id = 0, 0
        print >> sys.stdout, "graph FPTree {"
        print >> sys.stdout, "\t0 [label=\"root\"];"
        for node in self.root_node.sub_nodes:
            id = self.__print_tree_rec(node, nodeid, id)
        print >> sys.stdout, "}"

    def __print_tree_rec(self, node, parentid, id):
        nodeid = id + 1
        label = "%s: %i" % (node.item, node.count)
        print >> sys.stdout, "\t%i [label=\"%s\"];" % (nodeid, label)
        print >> sys.stdout, "\t%i -- %i;" % (parentid, nodeid)
        id += 1
        for sub_node in node.sub_nodes:
            id = self.__print_tree_rec(sub_node, nodeid, id)

        return id

class DataFileParser:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None

    def get_data(self):
        if self.data is None:
            self.data = open(self.data_file, "rb")
        line = self.data.readline()
        while line != "":
            yield line
            line = self.data.readline()
        yield line

    def reinit(self):
        if self.data is None:
            self.data = open(self.data_file, "rb")
        else:
            self.data.seek(0)

    def end(self):
        self.data.close()
        self.data = None


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:vs:t:i:",  \
               ["help", "output=", "verbose", "support=", "treshold=", "input="])
        except getopt.error, msg:
            raise Usage(msg)

        verbose = False
        output = "fpgrowth-results.out"
        input = "test.in"
        support = 3
        treshold = 0.20

        # Options processing
        for option, value in opts:
            if option in ("-v", "--verbose"):
                verbose = True
            elif option in ("-h", "--help"):
                raise Usage(HELP_MESSAGE)
            elif option in ("-o", "--output"):
                output = value
            elif option in ("-i", "--input"):
                input = value
            elif option in ("-s", "--support"):
                try:
                    support = int(value)
                except ValueError:
                    raise Usage("Support value must be of type integer")
            elif option in ("-t", "--treshold"):
                try:
                    treshold = float(value)
                except ValueError:
                    raise Usage("Treshold value must be of type float")

        fpgrowth = FPGrowth(support, treshold)
        data_parser = DataFileParser(input)
        fpgrowth.build_tree(data_parser)
        data_parser.end()
        frequent_patterns = fpgrowth.mine()

        results = [ (fp, frequent_patterns[fp]) for fp in frequent_patterns ]
        results.sort(cmp=lambda a,b: cmp(a[1], b[1]), reverse=True)

        output_file = open(output, "wb")

        print >> output_file, "Resulting frequent patterns:"

        if len(frequent_patterns) == 0:
            print >> output_file, "No frequent patterns found"

        for r in results:
            fp = r[0]
            count = r[1]
            i = 1
            for item in fp:
                output_file.write(item)

                if i < len(fp):
                    output_file.write(", ")
                i += 1
            print >> output_file, " (count: %i)" % count

        output_file.close()

        if verbose:
            fpgrowth.print_tree()

    except Usage, err:
        print >> sys.stderr, str(err.msg)
        print >> sys.stderr, "for help use --help"
        return 1

if __name__ == "__main__":
    sys.exit(main())

