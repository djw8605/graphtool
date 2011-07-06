#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.expandvars('$GRAPHTOOL_ROOT/src'))

from graphtool.tools.common import expand_string
from graphtool.graphs.common_graphs import ScatterPlot

import numpy
numpts = 100

data = {}
for site in ['Site A', 'Site B']:
    data1 = numpy.random.normal(size=numpts, loc=1.0)
    data2 = numpy.random.normal(size=numpts, loc=1.0)
    data3 = numpy.random.random(numpts)
    data[site] = {}
    for i in range(numpts):
        data[site][data1[i], data2[i]] = .1*data3[i]

metadata = {'title':'Scatter Plot Example'}

file = open(expand_string('$HOME/tmp/scatter.png',os.environ),'w')

SP = ScatterPlot()
SP(data, file, metadata)
