#!/usr/bin/env python
import os, random
from graphtool.graphs.common_graphs import HorizontalStackedBarGraph
from graphtool.tools.common import expand_string

# First example - we have a bar graph with text labels

data = {}

# Second example - bar graph with integer labels, bar width 2
entry1 = {}; entry2 = {}

for i in range(0,10,2):
    entry1[str(i)] = i**2
    entry2[str(i)] = i

data = {'Team A':entry1, 'Team B':entry2}

metadata = {'title':'Horizontal Stacked Bar Example',
            'title_size':20, 'text_size':17, 'fixed-height':False }

file = open(expand_string('$HOME/tmp/horizontal_stacked_bar.png',os.environ),'w')

HSBG = HorizontalStackedBarGraph()
HSBG(data, file, metadata)

