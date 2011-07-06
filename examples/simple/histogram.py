#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.expandvars('$GRAPHTOOL_ROOT/src'))

from graphtool.tools.common import expand_string
from graphtool.graphs.common_graphs import Histogram

import numpy
data = numpy.random.normal(size=100, loc=1.0)

metadata = {'title':'First Histogram Example', 'nbins': 15}

file = open(expand_string('$HOME/tmp/histogram.png',os.environ),'w')

HG = Histogram()
HG(data, file, metadata)
