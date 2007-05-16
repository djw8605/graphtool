#!/usr/bin/env python
import os
from graphtool.graphs.common_graphs import BarGraph
from graphtool.tools.common import expand_string

# First example - we have a bar graph with text labels

data = {'Team A':4, 'Team B':7}

print data

metadata = {'title':'First Bar Example', 'height':200, 'width':400,
            'title_size':20, 'text_size':17}

file = open(expand_string('$HOME/tmp/bar_strings.png',os.environ),'w')

BG = BarGraph()
BG(data, file, metadata)

# Second example - we have a bar graph with integer data

data = {}
for i in range(10):
    data[i] = i**2

print data

metadata = {'title':'Second Bar Example'}

file = open(expand_string('$HOME/tmp/bar_ints.png',os.environ),'w')

BG = BarGraph()
BG(data, file, metadata)
