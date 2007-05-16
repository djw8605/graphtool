#!/usr/bin/env python

import time, os, random, datetime
from matplotlib.dates import num2date
from graphtool.graphs.common_graphs import BarGraph, StackedBarGraph
from graphtool.graphs.graph import TimeGraph
from graphtool.tools.common import expand_string

span = 3600
max_value = 40
# Generate our time series
def make_time_data( ):
    end_time = time.time(); end_time -= end_time % span
    begin_time = end_time - 24*span
    data = {}
    for i in range(begin_time, end_time, span):
        data[i] = random.random()*max_value
    return begin_time, end_time, data

# Our classes
class TimeBarGraph( TimeGraph, BarGraph ):
    pass
    
class TimeStackedBarGraph( TimeGraph, StackedBarGraph ):
    pass

# Bar graph stuff.
TBG = TimeBarGraph()
begin_time, end_time, data = make_time_data()
metadata = {'title':'Bar Graph w.r.t. Time', 'starttime':begin_time, 'endtime':end_time, 'span':span }
filename = expand_string('$HOME/tmp/time_bar.png',os.environ)
file = open( filename, 'w' )
TBG( data, file, metadata )

# Stacked Bar graph stuff.
TSBG = TimeStackedBarGraph()
begin_time, end_time, data1 = make_time_data()
begin_time, end_time, data2 = make_time_data()
data = {'Team A': data1, 'Team B': data2}
metadata = {'title':'Stacked Bar Graph w.r.t. Time', 'starttime':begin_time, 'endtime':end_time, 'span':span }
filename = expand_string('$HOME/tmp/time_stacked_bar.png',os.environ)
file = open( filename, 'w' )
TSBG( data, file, metadata )
