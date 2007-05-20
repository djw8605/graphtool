#!/usr/bin/env python
import os, random
from graphtool.graphs.common_graphs import QualityBarGraph
from graphtool.tools.common import expand_string

# First example - we have a bar graph with text labels

data = {}

for i in range(40):
    data['Team %i' % i] = random.random()
    
metadata = {'title':'Quality Bar Example',
            'title_size':20, 'text_size':10, 'fixed-height':False }

file = open(expand_string('$HOME/tmp/quality_bar.png',os.environ),'w')

QBG = QualityBarGraph()
QBG(data, file, metadata)
