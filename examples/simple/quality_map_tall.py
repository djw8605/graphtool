#!/usr/bin/env python

import time, os, random, datetime
from matplotlib.dates import num2date
from graphtool.graphs.common_graphs import QualityMap
from graphtool.tools.common import expand_string

span = 3600

# Generate our time series
def make_time_data( ):
    end_time = time.time(); end_time -= end_time % span
    begin_time = end_time - 24*span
    data = {}
    for i in range(begin_time, end_time, span):
        data[i] = random.random()
    return begin_time, end_time, data

QM = QualityMap()

# Data generation
full_data = {}
for i in range(100):
    team_name = 'Team %i' % i
    begin_time, end_time, data = make_time_data()
    full_data[team_name] = data
    
metadata = {'title':'Tall Quality Plot w.r.t. Time', 'starttime':begin_time, 
            'endtime':end_time, 'span':span, 'fixed-height':False }
filename = expand_string('$HOME/tmp/quality_map_tall.png',os.environ)
file = open( filename, 'w' )
QM( full_data, file, metadata )
