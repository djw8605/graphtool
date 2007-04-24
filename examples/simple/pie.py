#!/usr/bin/env python

import os
from graphtool.graphs.common_graphs import PieGraph
from graphtool.tools.common import expand_string

filename = expand_string('$HOME/tmp/pie.png',os.environ)

file = open( filename, 'w' )

data = {'foo':45, 'bar':55}
metadata = {'title':'Hello Graphing World!'}
pie = PieGraph()
coords = pie.run( data, file, metadata )
