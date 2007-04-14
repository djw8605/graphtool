
import types, datetime, numpy, math
from graphtool.tools.common import to_timestamp, expand_string
from graphtool.graphs.graph import Graph, PivotGraph, PivotGroupGraph, TimeGraph
from graphtool.graphs.common import pretty_float
import matplotlib.cm as cm
from matplotlib.mlab import linspace
from matplotlib.dates import date2num
from matplotlib.patches import Polygon, Wedge, Shadow, Rectangle
from matplotlib.ticker import FixedLocator, FixedFormatter
from matplotlib.cbook import is_string_like
from matplotlib.colors import normalize
from pylab import setp

class BarGraph( PivotGraph ):

  bar_graph_space = .1

  def draw( self ):
    results = self.parsed_data
    if len( results.items() ) == 0:
      return None
    keys = self.sort_keys( results )
    first_key = keys[0]
    if type(first_key) == types.StringType: is_str = True
    tmp_x = []; tmp_y = []
    if is_str: counter = 0
    num_bars = len( keys )
    width = (1 - bar_graph_space) * float(self.width) / 86400.0 / num_bars
    offset = width*position + bar_graph_space / 2.0
    for pivot, data in results.items():
      if is_str:
        tmp_x.append( counter + offset )
        counter += 1
      else:
        tmp_x.append( pivot + offset )
      tmp_y.append( float(data) )
    self.bars = ax.bar( tmp_x, tmp_y, width=width, color=color )
    pivots = keys
    for idx in range(len(pivots)):
      self.coords[ pivots[idx] ] = self.bars[idx]

  def get_coords( self ):
    height = self.prefs['height']
    coords = self.coords
    keys = self.sort_keys( self.parsed_data )
    for pivot in keys:
      bar = coords[pivot]
      t = bar.get_transform()
      my_coords = t.seq_xy_tups( bar.get_verts() )
      coords[ pivot ] = tuple( (i[0],height-i[1]) for i in my_coords )
    return coords

class StackedBarGraph( PivotGroupGraph ):

  width = 86400.0

  is_timestamps = False

  def make_bottom_text( self ):
    units = str(self.metadata.pop('column_units','')).strip()
    agg_stats = {}
    results = self.parsed_data
    for link, groups in results.items():
      for timebin, value in groups.items():
        if agg_stats.has_key(timebin):
          agg_stats[timebin] += value
        else:
          agg_stats[timebin] = value
    values = agg_stats.values()
    try: data_max = max(values)
    except: data_max = False
    try: data_min = min(values)
    except: data_min = False
    try: data_average = numpy.average( values )
    except: data_average = False
    try:
      last_time = max( agg_stats.keys() )
      data_current = agg_stats[last_time]
    except: data_current = False
    retval = ''
    if data_max != False: retval += "Maximum: " + pretty_float( data_max ) + " " + units
    if data_min != False: retval += ", Minimum: " + pretty_float( data_min ) + " " + units
    if data_average != False: retval += ", Average: " + pretty_float( data_average ) + " " + units
    if data_current != False: retval += ", Current: " + pretty_float( data_current ) + " " + units
    return retval

  def draw( self ):
    results = self.parsed_data
    bottom = None
    colors = list(self.colors)
    coords = self.coords
    keys = self.sort_keys( results ); keys.reverse()
    for pivot,color in zip(keys,colors):
      bottom, bars = self.make_stacked_bar( results[pivot], bottom, color )
      groups = results[pivot].keys(); groups.sort() 
      coords[pivot] = {}
      bar_dict = {}
      for bar in bars:
        bar_dict[ bar.get_verts()[0][0] ] = bar
      bars_keys = bar_dict.keys(); bars_keys.sort() 
      for idx in range(len(groups)):
        coords[pivot][groups[idx]] = bar_dict[ bars_keys[idx] ]

  def make_stacked_bar( self, points, bottom, color ):
    if bottom == None:
      bottom = {}
    tmp_x = []; tmp_y = []; tmp_b = []

    for key in points.keys():
      if self.is_timestamps:
        key_date = datetime.datetime.utcfromtimestamp( key )
        key_val = date2num( key_date )
      else:
        key_val = key
      tmp_x.append( key_val )
      tmp_y.append( points[key] )
      if not bottom.has_key( key ):
        bottom[key] = 0
      tmp_b.append( bottom[key] )
      bottom[key] += points[key]
    if len( tmp_x ) == 0:
      return bottom, None
    width = float(self.width) / 86400.0
    bars = self.ax.bar( tmp_x, tmp_y, bottom=tmp_b, width=width, color=color )
    setp( bars, linewidth=0.5 )
    return bottom, bars

  def get_coords( self ):
    coords = self.coords
    keys = self.sort_keys( self.parsed_data )
    for pivot in keys:
      groupings = coords[pivot]
      for group, p in groupings.items():
        t = p.get_transform()
        my_coords = t.seq_xy_tups( p.get_verts() )
        height = self.prefs['height']
        coords[pivot][group] = tuple( (i[0],height-i[1]) for i in my_coords )
    self.coords = coords
    return coords

class CumulativeGraph( TimeGraph, PivotGroupGraph ):
 
  def make_bottom_text( self ):
    results = self.results 
    units = str(self.metadata.pop('column_units','')).strip()
    agg_stats = {} 
    data_max = 0
    for pivot, groups in results.items():
      timebins = groups.keys(); timebins.sort()
      data_max += groups[ timebins[-1] ]
  
    timespan = (self.end_num - self.begin_num)*86400.0

    retval = "Total: " + pretty_float( data_max ) + " " + units
    retval += ", Average Rate: " + pretty_float( data_max / timespan ) + " " + units + "/s"
    return retval

  def setup( self ):

    super( CumulativeGraph, self ).setup()

    results = self.results
    
    is_cumulative = self.metadata.pop( 'is_cumulative', False )

    if not is_cumulative:
      raise Exception( "Data passed to cumulative graph not marked as cumulative." )

  def make_stacked_line( self, points, bottom, color ):

    span = self.width
    ax = self.ax
    begin = self.begin; end = self.end
    if bottom == None: bottom = {}

    new_points = {}
    if self.is_timestamps:
      for group, data in points.items():
        key_date = datetime.datetime.utcfromtimestamp( group )
        key_val = date2num( key_date )
        new_points[ key_val ] = data
      points = new_points
      begin = date2num( datetime.datetime.utcfromtimestamp( self.begin ) )
      end = date2num( datetime.datetime.utcfromtimestamp( self.end ) )

    min_key = min(points.keys())
    if min_key - begin > span:
      points[min_key-span] = 0
    
    # Get the union of all times:
    times_set = set( points.keys() )
    times_set = times_set.union( bottom.keys() )
    times_set.add( end )
    times_set.add( begin )
     
    my_times = list( times_set ); my_times.sort(); my_times.reverse()
      
    bottom_keys = list(bottom.keys()); bottom_keys.sort()
    points_keys = list(points.keys()); points_keys.sort()

    polygons = []; seq = []; next_bottom = {}
    if len( bottom.keys() ) > 0:
      prev_bottom_val = max( bottom.values() )
    else:
      prev_bottom_val = 0
    if len( points.keys() ) > 0:
      prev_val = max( points.values() )
    else:
      prev_val = 0
    prev_key = my_times[-1]
    for key in my_times:
      if not bottom.has_key( key ):
        my_bottom_keys = list(bottom_keys)
        my_bottom_keys.append( key )
        my_bottom_keys.sort()
        if my_bottom_keys[0] == key:
          bottom[key] = 0
        else:
          next_key = my_bottom_keys[ my_bottom_keys.index(key)-1 ]
          next_val = bottom[ next_key ]
          bottom[key] = (prev_bottom_val - next_val)*(key-next_key)/float(prev_key-next_key) + next_val
      if not points.has_key( key ):
        if key <= points_keys[0] and key != end:
          points[key] = 0
        else:
          points[key] = prev_val
      prev_bottom_val = bottom[key]
      prev_val = points[key]
      prev_key = key
      val = points[key] + bottom[key]
      next_bottom[key] = val
      y = val
      x = key
      seq.append( (x,y) )
      next_bottom[key] = val
    my_times.reverse()
    for key in my_times:
      y = float(bottom[key])
      x = key
      seq.append( (x,y) )
    poly = Polygon( seq, facecolor=color, fill=True, linewidth=.5 )
    ax.add_patch( poly )
    polygons.append( poly )
    new_ymax = max(max(next_bottom.values())+.5, ax.axis()[3])
    ax.set_xlim( xmin=float(my_times[0]), xmax=float(my_times[-1]) )
    ax.set_ylim( ymax = new_ymax )
    return next_bottom, polygons

  def draw( self ):

    results = self.results
    colors = self.colors
    bottom = None
    coords = self.coords
    keys = self.sort_keys( results ); keys.reverse()
    for link, color in zip(keys,colors):
      bottom, bars = self.make_stacked_line( results[link], bottom, color )
      coords[ link ] = bars[0]  

  def get_coords( self ):
    results = self.results
    links = self.coords
    if len(links.keys()) == 0: return None

    height = self.prefs['height']
    coords = {}
    for link in links:
      coords[link] = {}
    transform = links.values()[0].get_transform()
    timebins = results.values()[0].keys(); timebins.sort()
    timebins_num = [date2num( datetime.datetime.utcfromtimestamp( to_timestamp( timebin ) ) ) for timebin in timebins]
    keys = self.sort_keys( results ); keys.reverse()
    for idx in range(len(timebins)-1):
      timebin = timebins[idx]
      timebin_next = timebins[idx+1]
      timebin_num = timebins_num[idx]
      csum_left = 0; csum_right = 0
      for pivot in keys:
        groups = results[pivot]
        time_begin = timebin_num
        time_end = time_begin + self.width/86400.0
        size_left = groups[timebin]
        size_right = groups[timebin_next]
        bottom_left = csum_left
        csum_left += size_left
        bottom_right = csum_right
        csum_right += size_right
        my_coords = transform.seq_xy_tups( [(time_begin, bottom_left), (time_begin, csum_left), \
                    (time_end, csum_right), (time_end, bottom_right), (time_begin, bottom_left)] )
        coords[pivot][timebin] = tuple( (i[0],height-i[1]) for i in my_coords )
    timebin = timebins[-1]
    timebin_num = timebins_num[-1]
    csum_left = 0; csum_right = 0
    for pivot in keys:
      groups = results[pivot]
      time_begin = timebin_num
      time_end = self.end_num
      size_left = groups[timebin]
      bottom_left = csum_left
      csum_left += size_left
      my_coords = transform.seq_xy_tups( [(time_begin, bottom_left), (time_begin, csum_left), \
                  (time_end, csum_left), (time_end, bottom_left), (time_begin, bottom_left)] )
      coords[pivot][timebin] = tuple( (i[0],height-i[1]) for i in my_coords )

    self.coords = coords
    return coords

class PieGraph( PivotGraph ):

  def pie(self, x, explode=None, labels=None,
            colors=None,      
            autopct=None,
            pctdistance=0.6,
            shadow=False
            ):
            
        x = numpy.array(x, numpy.float64)

        sx = float(numpy.sum(x))
        if sx>1: x = numpy.divide(x,sx)
            
        if labels is None: labels = ['']*len(x)
        if explode is None: explode = [0]*len(x)
        assert(len(x)==len(labels))
        assert(len(x)==len(explode))
        if colors is None: colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')

        center = 0,0
        radius = 1
        theta1 = 0
        i = 0   
        texts = []
        slices = []
        autotexts = []
        for frac, label, expl in zip(x,labels, explode):
            x, y = center 
            theta2 = theta1 + frac
            thetam = 2*math.pi*0.5*(theta1+theta2)
            x += expl*math.cos(thetam)
            y += expl*math.sin(thetam)
            
            w = Wedge((x,y), radius, 360.*theta1, 360.*theta2,
                      facecolor=colors[i%len(colors)])
            slices.append(w)
            self.ax.add_patch(w)
            w.set_label(label)
            
            if shadow:
                # make sure to add a shadow after the call to
                # add_patch so the figure and transform props will be
                # set
                shad = Shadow(w, -0.02, -0.02,
                              #props={'facecolor':w.get_facecolor()}
                              )
                shad.set_zorder(0.9*w.get_zorder())
                self.ax.add_patch(shad)

            
            xt = x + 1.1*radius*math.cos(thetam)
            yt = y + 1.1*radius*math.sin(thetam)
            
            thetam %= 2*math.pi
            
            if 0 <thetam and thetam < math.pi:
                valign = 'bottom'
            elif thetam == 0 or thetam == math.pi:
                valign = 'center'
            else:
                valign = 'top'
            
            if thetam > math.pi/2.0 and thetam < 3.0*math.pi/2.0:
                halign = 'right'
            elif thetam == math.pi/2.0 or thetam == 3.0*math.pi/2.0:
                halign = 'center'
            else:
                halign = 'left'
            
            t = self.ax.text(xt, yt, label,
                          size=self.prefs['subtitle_size'],
                          horizontalalignment=halign,
                          verticalalignment=valign)
            
            t.set_family( self.prefs['font_family'] )
            t.set_fontname( self.prefs['font'] )
            t.set_size( self.prefs['subtitle_size'] )
            
            texts.append(t)
            
            if autopct is not None:
                xt = x + pctdistance*radius*math.cos(thetam)
                yt = y + pctdistance*radius*math.sin(thetam)
                if is_string_like(autopct):
                    s = autopct%(100.*frac)
                elif callable(autopct):
                    s = autopct(100.*frac)
                else:                    raise TypeError('autopct must be callable or a format string')
                
                t = self.ax.text(xt, yt, s,
                              horizontalalignment='center',
                              verticalalignment='center')
                
                t.set_family( self.prefs['font_family'] )
                t.set_fontname( self.prefs['font'] )
                t.set_size( self.prefs['subtitle_size'] )
                
                autotexts.append(t)

            
            theta1 = theta2
            i += 1
        
        self.ax.set_xlim((-1.25, 1.25))
        self.ax.set_ylim((-1.25, 1.25))
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        self.ax.set_frame_on(False)

        if autopct is None: return slices, texts
        else: return slices, texts, autotexts

  min_amount = .1

  def setup( self ):
    super( PieGraph, self ).setup()

    results = self.results
    parsed_data = self.results

    column_units = getattr( self, 'column_units', self.metadata.get('column_units','') )
    sql_vars = getattr( self, 'vars', {} )
    title = getattr( self, 'title', self.metadata.get('title','') )

    title = title + ' (Sum: %i ' + column_units.strip() + ')'
    title = expand_string( title, sql_vars )
  
    labels = []
    amt = [] 
    keys = self.sort_keys( parsed_data )
    for key in keys:
      labels.append( str(key) + (' (%i)' % float(parsed_data[key])) )
      amt.append( float(parsed_data[key]) )
    self.labels = labels
    self.labels.reverse()
    self.title = title % float(sum(amt))
    self.amt_sum = float(sum(amt))
    self.amt = amt

    #labels.reverse()

  def prepare_canvas( self ):
    self.ylabel = ''
    self.kw['square_axis'] = True
    self.kw['watermark'] = False
    super( PieGraph, self ).prepare_canvas()

  def draw( self ):
    amt = self.amt
    results = self.results
    my_labels = []
    local_labels = list(self.labels); local_labels.reverse()
    for label in local_labels:
      orig_label = label.rsplit(' ',1)[0]
      val = float(results[orig_label])
      if val / self.amt_sum > self.min_amount:
        my_labels.append( orig_label )
      else:
        my_labels.append( "" )

    def my_display( x ):
      if x > 100*self.min_amount:
        my_amt = int(x/100.0 * self.amt_sum )
        return str(my_amt)
      else:
        return ""

    explode = [.1 for i in amt]

    self.colors.reverse()
   
    self.wedges, text_labels, percent = self.pie( amt, explode=explode, labels=my_labels, shadow=True, colors=self.colors, autopct=my_display )
    
  def get_coords( self ):
    try:
      coords = self.coords
      height = self.prefs['height']
      wedges = self.wedges
      labels = self.labels
      wedges_len = len(wedges)
      for idx in range(wedges_len):
        orig_label =  labels[idx].rsplit(' ',1)[0]
        wedge = wedges[ wedges_len - idx - 1 ]
        v = wedge.get_verts()
        t = wedge.get_transform()
        my_coords = t.seq_xy_tups( v )
        coords[ orig_label ] = tuple( (i[0],height-i[1]) for i in my_coords )
      self.coords = coords
      return coords
    except:
      return None

# TODO this is not generic...
class QualityMap( TimeGraph, PivotGroupGraph ):

  sort_keys = Graph.sort_keys

  def setup( self ):

    super( QualityMap, self ).setup()

    results = self.parsed_data
    self.try_column =  int( self.metadata.pop('try_column',0)  ) 
    self.done_column = int( self.metadata.pop('done_column',1) )
    self.fail_column = int( self.metadata.pop('fail_column',2) )

    # Rearrange our data
    timebins = set()
    for link in self.sort_keys( results ):
      for timebin in results[link].keys():
        timebins.add( timebin )
    links = self.sort_keys(results); 
    links.reverse(); timebins = list(timebins)
    links_lu = {}; timebins_lu = {}
    counter = 0
    for link in links: links_lu[link] = counter; counter += 1
    counter = 0
    for bin in timebins: timebins_lu[bin] = counter; counter += 1

    # Setup the colormapper to get the right colors
    norms = normalize(0,100)
    mapper = cm.ScalarMappable( cmap=cm.RdYlGn, norm=norms )
    A = linspace(0,100,100)
    mapper.set_array(A)
    self.links = links
    self.links_lu = links_lu
    self.mapper = mapper

  def prepare_canvas( self ):
    self.legend = False
    super( QualityMap, self ).prepare_canvas()
    setp( self.ax.get_yticklines(), markeredgewidth=0.0 )

    links = self.links

    # Make horizontal and vertical light grey lines every 3 ticks:
    lineskip = 2
    len_links = len(self.links); #len_ticks = len(ticks)
    for line_num in range(1,len_links):
      if (len_links - line_num) % lineskip == 0:
        self.ax.plot( [self.begin_num, self.end_num], [line_num, line_num], linewidth=1.0, color='k', linestyle=':' )
    self.ax.xaxis.grid(True)
    self.ax.yaxis.grid(False)
    #self.ax.set_xlim( xmin=self.begin_num, xmax=self.end_num )
    self.ax.set_ylim( ymin=0, ymax=len(links) )

  def draw( self ):

    coords = self.coords
    ax = self.ax
    links = self.links
    links_lu = self.links_lu
    try_column, done_column, fail_column = self.try_column, self.done_column, self.fail_column
    results = self.parsed_data
    for link in self.sort_keys( results ):
      coords[link] = {}
      for timebin in results[link].keys():
        data = results[link][timebin]
        try:
          try_files, done, fail = data[try_column], data[done_column], data[fail_column]
        except Exception, e:
          continue
        if float(done) > 0:
          value = done / float( fail + done )
        else:
          value = 0.0
        if done >= 0 or fail >= 0:
          left = date2num( datetime.datetime.utcfromtimestamp( float(timebin) ) )
          bottom = links_lu[link]
          color = self.mapper.to_rgba( value*100 )
          p = Rectangle( (left, bottom), self.width/86400.0, 1.0, fill=True, fc=color )
          ax.add_patch(p)
          p.set_linewidth( 0.25 )
          t = p.get_transform()
          coords[link][timebin] = p

    y_vals =  numpy.arange(.5,len(links)+.5,1)
    fl = FixedLocator( y_vals )
    if self.kind.lower() == "link":
      links = [ i[0] + ' to ' + i[1] for i in links ]

    # Make the colorbar
    cb = self.fig.colorbar( self.mapper, format="%d%%", orientation='horizontal', fraction=0.04, pad=0.13, aspect=40  )
    setp( cb.outline, linewidth=.5 )
    setp( cb.ax.get_xticklabels(), size=10 )
    setp( cb.ax.get_xticklabels(), family=self.prefs['font_family'] )
    setp( cb.ax.get_xticklabels(), fontname = self.prefs['font'] )

    # Make the formatter for the y-axis
    ff = FixedFormatter( links )
    ax.yaxis.set_major_formatter( ff )
    ax.yaxis.set_major_locator( fl )

    # Calculate the spacing of the y-tick labels:
    height_per = ax.get_position()[-1]
    height_inches = self.fig.get_size_inches()[-1] * height_per
    height_pixels = self.fig.get_dpi() * height_inches
    max_height_labels = height_pixels / max( 1, len(links) )

    # Adjust the font height to match the maximum available height
    font_height = max_height_labels * 1.7 / 3.0 - 1.0
    font_height = min( font_height, 7 )
    setp( ax.get_yticklabels(), size=font_height )

    ax.yaxis.draw( self.canvas.get_renderer() )

    total_xmax = 0
    for label in ax.get_yticklabels():
      bbox = label.get_window_extent( self.canvas.get_renderer() )
      total_xmax = max( bbox.xmax()-bbox.xmin(), total_xmax )
    move_left = (total_xmax+4) / self.prefs['width']
    pos = ax.get_position()
    pos[0] = move_left
    pos[2] = 1 - pos[0] - .02
    ax.set_position( pos )

  def get_coords( self ):

    coords = self.coords
    height = self.prefs['height']
    keys = self.sort_keys( self.parsed_data )
    for pivot in keys:
      groups = coords[pivot] 
      for group, p in groups.items():
        t = p.get_transform()
        my_coords = t.seq_xy_tups( p.get_verts() )
        coords[pivot][group] = tuple( (i[0],height-i[1]) for i in my_coords )

    return coords

