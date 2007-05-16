import time, os, random, datetime
from graphtool.graphs.common_graphs import CumulativeGraph
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

# Create and plot cumulative plot.
CG = CumulativeGraph()
begin_time, end_time, data1 = make_time_data()
begin_time, end_time, data2 = make_time_data()
data = {'Team A': data1, 'Team B': data2}
metadata = {'title':'Some Cumulative Data', 'starttime':begin_time, 'endtime':end_time, 'span':span, 'is_cumulative':False }
filename = expand_string('$HOME/tmp/cumulative.png',os.environ)
file = open( filename, 'w' )
CG( data, file, metadata )
