#!/usr/bin/env python
import os
from graphtool.graphs.common_graphs import StackedBarGraph
from graphtool.tools.common import expand_string

# First example - we have a bar graph with text labels
entry1 = {'foo':3, 'bar':5}
entry2 = {'foo':4, 'bar':6}

data = {'Team A':entry1, 'Team B':entry2}

metadata = {'title':'First Stacked Bar Example'}

file = open(expand_string('$HOME/tmp/stacked_strings.png',os.environ),'w')

SBG = StackedBarGraph()
SBG(data, file, metadata)

# Second example - bar graph with integer labels, bar width 2
entry1 = {}; entry2 = {}

for i in range(0,10,2):
    entry1[i] = i**2
    entry2[i] = i

data = {'Team A':entry1, 'Team B':entry2}

metadata = {'title':'Second Stacked Bar Example', 'span':2}

del entry1[6]; del entry2[6]; del entry2[8]

entry1[0] = 4

print data

file = open(expand_string('$HOME/tmp/stacked_ints.png',os.environ),'w')
SBG = StackedBarGraph()
SBG(data, file, metadata)
