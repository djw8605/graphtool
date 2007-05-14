#!/usr/bin/env python
import os, random
from graphtool.graphs.common_graphs import HorizontalBarGraph
from graphtool.tools.common import expand_string

# First example - we have a bar graph with text labels

data = {}

for i in range(40):
    data['Team %i' % i] = random.random() * 10
    
metadata = {'title':'Horizontal Bar Example',
            'title_size':20, 'text_size':17, 'fixed-height':False }

file = open(expand_string('$HOME/tmp/horizontal_bar.png',os.environ),'w')

HBG = HorizontalBarGraph()
HBG(data, file, metadata)
