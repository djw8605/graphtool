#!/usr/bin/env python


import os
import sys
import time
import random
import datetime

sys.path.insert(0, os.path.expandvars('$GRAPHTOOL_ROOT/src'))

from matplotlib.dates import num2date

from graphtool.graphs.common_graphs import QualityMap
from graphtool.tools.common import expand_string

span = 3600
values = [0, .25, .5, 1.0]
legend = {'Bad': 'red',
          'OK': 'yellow',
          'Good': 'green',
          'Unknown': 'grey',
          }
# Generate our time series
def make_time_data( ):
    end_time = time.time(); end_time -= end_time % span
    begin_time = end_time - 24*span
    data = {}
    for i in range(begin_time, end_time, span):
        data[i] = random.sample(values, 1)[0]
    return begin_time, end_time, data

QM = QualityMap()

# Data generation
full_data = {}
for i in range(10):
    team_name = 'Team %i' % i
    begin_time, end_time, data = make_time_data()
    full_data[team_name] = data
    
metadata = {'title':'Quality Plot w.r.t. Time', 'starttime':begin_time, 
            'endtime':end_time, 'span':span,
            'color_override': {0: 'grey',
                               .25: 'red',
                               .5: 'yellow',
                               1.0: 'green'},
             'legend': legend,
            }

filename = expand_string('$HOME/tmp/quality_map_dashboard.png',os.environ)
file = open( filename, 'w' )
QM( full_data, file, metadata )
