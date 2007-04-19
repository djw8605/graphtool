
import numpy, cStringIO, StringIO, traceback, time, datetime, warnings, types, os
import Image as PILImage, ImageEnhance as PILImageEnhance
import graphtool.graphs.common as common 
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator
from matplotlib.backends.backend_svg import RendererSVG
from matplotlib.patches import Wedge, Shadow, Rectangle, Polygon
from matplotlib.numerix import Float32
from matplotlib.pylab import setp
from graphtool.tools.common import to_timestamp, expand_string
from graphtool.tools.cache import Cache
from graphtool.database.query_handler import QueryHandler
from matplotlib.dates import date2num

cStringIO_type = type(cStringIO.StringIO())

prefs = {
  'text_size' : 7,    #in pixels
  'text_padding' : 3, #in pixels
  'legend_padding' : .01, # In percent of screen space / 100
  'figure_padding' : .10,
  'width' : 800,  #in pixels
  'height' : 500,
  'width_inches' : 8,    # Somewhat arbitrary, as dpi is adjusted to 
                       # fit the pixel sizes requested above.
  'columns' : 5,    # The number of columns to use in the legend 
  'max_rows' : 9,  # Maximum number of rows in the legend
  'title_size' : 14, # In pixels
  'subtitle_size' : 10,
  'font' : 'Lucida Grande',
  'font_family' : 'sans-serif',
  'square_axis' : False,
  'watermark' : '$GRAPHTOOL_ROOT/static_content/CMSbwl3.png'
}

def draw_empty( text, file, kw ):
  prefs = dict(globals()['prefs'])
  for key, data in kw.items():
    prefs[key] = data
  fig = Figure()
  canvas = FigureCanvasAgg( fig )
  dpi = prefs['width'] /prefs['width_inches']
  height_inches = prefs['height'] / float(dpi)
  fig.set_size_inches( prefs['width_inches'], height_inches )
  fig.set_dpi( dpi )
  fig.set_facecolor('white')
  fig.text( .5, .5, text, horizontalalignment='center' )
  if isinstance( file , StringIO.StringIO ) or type(file) == cStringIO_type:
    canvas.draw()
    size = canvas.get_renderer().get_canvas_width_height()
    buf=canvas.tostring_argb()
    im=PILImage.fromstring('RGBA', size, buf, 'raw', 'RGBA', 0, 1)
    a, r, g, b = im.split()
    im = PILImage.merge( 'RGBA', (r, g, b, a) )
    im.save( file, format = 'PNG' )
  else:
    canvas.print_figure(  file, **kw )

def find_info( attr, kw, metadata ):
  str_attr = str(attr)
  return kw.get( str_attr, metadata.get( str_attr, '' ) )

class Grapher( Cache,QueryHandler ):

  """ Thread-safe, caching grapher.  Simply call "do_graph" to
      make the graph.
  """

  def __init__( self, *args, **kw ):
    super( Grapher, self ).__init__( *args, **kw )
    for query in self.objs:
      query.metadata['grapher'] = self
    for query in self.known_commands.values():
      query.metadata['grapher'] = self

  def get_coords( self, query, metadata, **kw ):
    hash_str = self.make_hash_str( query, **kw )

    graph = self.do_graph( query, metadata, True, **kw )
    cache_data = self.check_cache( hash_str )
    if cache_data:
      return cache_data[0]
    else:
      return None

  def pre_command( self, query, *args, **kw ):
    hash_str = self.make_hash_str( query, **kw )
    results = self.check_cache( hash_str )
    if results: return results[1]

  def handle_results( self, results, metadata, *args, **kw ):
    return self.do_graph( results, metadata, **kw )

  def do_graph( self, obj, metadata, is_query=False, **kw ):
    if is_query: query = obj
    else: query = metadata['query']
    hash_str = self.make_hash_str( query, **kw )

    graphing_lock = self.check_and_add_progress( hash_str )
    
    if graphing_lock:
      graphing_lock.acquire()
      results = self.check_cache( hash_str )[1]
      graphing_lock.release()
      return results
    else:
      results =  self.check_cache( hash_str )
      if results:
        self.remove_progress( hash_str )
        return results[1]
      if is_query:
        try:
          results, metadata = query( **kw )
        except Exception, e:
          self.remove_progress( hash_str )
          raise e
      else:
        results = obj
      if 'graph_type' in metadata:
        try:
          graph_name = metadata['graph_type']
          graph = self.globals[ graph_name ]
          file = cStringIO.StringIO()
          graph_instance = graph() 
          graph_results = graph_instance.run( results, file, metadata, **kw )
        except Exception, e:
          self.remove_progress( hash_str )
          st = cStringIO.StringIO()
          traceback.print_exc( file=st )
          raise Exception( "Error in creating graph, hash_str:%s\n%s\n%s" % (hash_str, str(e), st.getvalue()) )
        self.add_cache( hash_str, (graph_results, file.getvalue()) )
      self.remove_progress( hash_str )
      return file.getvalue()

warnings.filterwarnings('ignore', 'integer argument expected, got float')

class Graph( object ):

  def __init__( self, *args, **kw ):
    super( Graph, self ).__init__( *args, **kw )
    self.sorted_keys = None

  def __call__( *args, **kw ):
    return run( *args, **kw )

  def run( self, results, file, metadata, **kw ):
    self.prefs = dict(prefs)
    self.kw = kw
    self.file = file
    self.results = results
    self.metadata = metadata
    self.coords = {}
    self.parse_data( )
    self.setup( )
    if len( self.parsed_data.keys() ) > 0:
      self.prepare_canvas( )
      self.draw( )
    else:
      self.draw_empty()
    self.write_graph( )
    self.get_coords( )
    return getattr( self, 'coords', None )

  def make_bottom_text( self ):
    return None

  def sort_keys( self, results, ignore_cache=False ):
    if self.sorted_keys != None and (not ignore_cache):
      return self.sorted_keys
    mykeys = list( results.keys() ); mykeys.sort()
    self.sorted_keys = mykeys
    return mykeys

  def setup( self ):
    self.colors = self.preset_colors( self.sort_keys( self.parsed_data ) )
    pass

  def parse_data( self ):
    self.parsed_data = dict( self.results )

  def draw_empty( self ):
    prefs = self.prefs
    fig = Figure()
    canvas = FigureCanvasAgg( fig )
    dpi = prefs['width'] /prefs['width_inches']
    height_inches = prefs['height'] / float(dpi)
    fig.set_size_inches( prefs['width_inches'], height_inches )
    fig.set_dpi( dpi )
    fig.set_facecolor('white')
    fig.text( .5, .5, "No data returned by DB query.", horizontalalignment='center' )
    self.ax = None
    self.fig = fig
    self.canvas = canvas

  hex_colors = [ "#e66266", "#fff8a9", "#7bea81", "#8d4dff", "#ffbc71", "#a57e81",
                 "#baceac", "#00ccff", "#ccffff", "#ff99cc", "#cc99ff", "#ffcc99",
                 "#3366ff", "#33cccc" ]

  def preset_colors( self, labels ):
    size_labels = len( labels )
    hex_colors = self.hex_colors
    size_colors = len( hex_colors )
    return [ hex_colors[ i % size_colors ] for i in range( size_labels ) ]

  def prepare_canvas( self ):
    self.bottom_text = self.make_bottom_text()
    title = getattr( self, 'title', '' )
    xlabel = getattr( self, 'xlabel', '' )
    ylabel = getattr( self, 'ylabel', '' )
    labels = getattr( self, 'labels', [] )
    colors = getattr( self, 'colors', [] )
    formatter_cb = getattr( self, 'formatter_cb', lambda x: None )
    legend = getattr( self, 'legend', True )
    bottom_text = getattr( self, 'bottom_text', None )
    kw = self.kw

    if type(legend) == types.StringType and legend.lower().find('f') > -1:
      legend = False
    elif type(legend) == types.StringType:
      legend = True
  
    prefs = self.prefs
    if 'svg' in kw.keys():
      svg = kw['svg']
    else: 
      svg = False
    if svg:
      FigureCanvas = FigureCanvasSVG
    else:
      FigureCanvas = FigureCanvasAgg
    for key in prefs.keys():
      if key in kw.keys():
        my_type = type( prefs[key] )
        prefs[key] = my_type(kw[key])
  
    # Alter the number of label columns, if necessary:
    max_length = 0
    for label in labels:
      max_length = max( len(label), max_length )
    
    if max_length > 23: prefs['columns'] = min( 4, prefs['columns'] )
    if max_length > 30: prefs['columns'] = min( 3, prefs['columns'] )
    if max_length > 37: prefs['columns'] = min( 2, prefs['columns'] )

    # Various size calculations
    num_labels = len( labels )
    dpi = prefs['width'] /prefs['width_inches']
    height_inches = prefs['height'] / float(dpi)
    legend_width = 1 - 2 * prefs['legend_padding']
    rows = max(1,min( numpy.ceil(num_labels / float(prefs['columns'])), prefs['max_rows']) + 2*int(bottom_text != None))
    if not legend:
      rows = 0.0
    legend_height = (2*prefs['text_padding'] + prefs['text_size']) * rows/float(prefs['height'])
    leg_pix_height = legend_height * height_inches          * dpi
    leg_pix_width =  legend_width  * prefs['width_inches']  * dpi
    column_width = 1.0 / float( prefs['columns'] )
    if legend:
      column_height = (2 * prefs['text_padding'] + prefs['text_size']) / leg_pix_height
    else:
      column_height = 0.0
    box_width = prefs['text_size']
    if legend:
      bottom = 2 * prefs['legend_padding'] + legend_height
    else:
      bottom = 0.0

    # Create our figure and canvas to work with
    fig = Figure()
    canvas = FigureCanvas( fig )

    # Set the figure properties we derived above.
    fig.set_size_inches( prefs['width_inches'], height_inches )
    fig.set_dpi( dpi )

    fig.set_facecolor('white')

    # rect = (left, bottom, width, height)
    legend_rect = prefs['legend_padding'], prefs['legend_padding'], legend_width, legend_height
    if prefs['square_axis']:
      min_size = min( 1 - 1.5*prefs['figure_padding'], 1 - bottom - 2*prefs['figure_padding'] )
      ax_rect = (.5 - min_size/2.0*prefs['height']/float(prefs['width']), prefs['figure_padding'] + bottom, prefs['height']/float(prefs['width'])*min_size, min_size )
    else:
      ax_rect = (prefs['figure_padding'], prefs['figure_padding'] + bottom, 1 - 1.5*prefs['figure_padding'], \
                 1 - bottom - 2*prefs['figure_padding'])

    # Add a watermark:
    if 'watermark' in prefs.keys() and str(prefs['watermark']) != 'False':
      #box = (.8,0,.2,.2)
      box = (0,0,prefs['height']/float(prefs['width']),1)
      i = PILImage.open( os.path.expandvars( os.path.expanduser( prefs['watermark'] ) ) )
      enh = PILImageEnhance.Contrast( i )
      i = enh.enhance( .033 )
      ax_wm = fig.add_axes( box  )
      im = ax_wm.imshow( i, origin='lower', aspect='equal' )
      ax_wm.axis('off')
      ax_wm.set_frame_on( False )
      ax_wm.set_clip_on( False )

    # Create our two axes, and set properties
    ax = fig.add_axes( ax_rect )
    frame = ax.get_frame()
    frame.set_fill( False )
    setp( ax.get_xticklabels(), family=prefs['font_family'] )
    setp( ax.get_xticklabels(), fontname=prefs['font'] )
    setp( ax.get_xticklabels(), size=prefs['text_size'] )

    setp( ax.get_yticklabels(), family=prefs['font_family'] )
    setp( ax.get_yticklabels(), fontname=prefs['font'] )
    setp( ax.get_yticklabels(), size=prefs['text_size'] )

    setp( ax.get_xticklines(),  markeredgewidth=2.0 )
    setp( ax.get_yticklines(),  markeredgewidth=2.0 )
    setp( ax.get_xticklines(),  zorder=4.0 )

    if legend: legend_ax = fig.add_axes( legend_rect )
    ax.grid( True, color='#555555', linewidth=0.1 )
    if legend: legend_ax.set_axis_off()

    # Set text on main axes.
    # Creates a subtitle, if necessary 
    title = title.split('\n',1)
    if len(title) == 1:
      ax.set_title( title[0] )
    else:
      ax.set_title( title[0] + '\n' )
      ax.title.set_transform( ax.transAxes )
      ax.title.set_clip_box( None )
      ax._set_artist_props( ax.title )
      ax.subtitle = ax.text( 0.5, 1.02, title[1],
          verticalalignment='bottom',
          horizontalalignment='center' )
      ax.subtitle.set_family( prefs['font_family'] )
      ax.subtitle.set_fontname( prefs['font'] )
      ax.subtitle.set_size(prefs['subtitle_size'])
      ax.subtitle.set_transform( ax.transAxes )
      ax.subtitle.set_clip_box( None )
    ax.title.set_family( prefs['font_family'] )
    ax.title.set_fontname( prefs['font'] )
    ax.title.set_weight('bold')
    ax.title.set_size( prefs['title_size'] )

    # Set labels
    t = ax.set_xlabel( xlabel )
    t.set_family( prefs['font_family'] )
    t.set_fontname( prefs['font'] )

    t = ax.set_ylabel( ylabel )
    t.set_family( prefs['font_family'] )
    t.set_fontname( prefs['font'] )

    # Now, make the legend.
    offset = 0
    early_stop = False
    zipped = zip(labels,colors); zipped.reverse()
    for my_text, my_color in zipped:
      # Size calculations
      left = (box_width+3*prefs['text_padding'])/leg_pix_width + \
              column_width*(offset % prefs['columns'])
      top = 1 - (column_height)*(numpy.floor( offset / prefs['columns'] ))
      next_bottom = 1 - (column_height)*(numpy.floor((offset+1)/prefs['columns'])+1 + 2*int(bottom_text != None))

      # Stop early if we ran out of room.
      if next_bottom < 0 and (num_labels - offset > 1):
        early_stop = True
        break

      # Create text
      if legend:
        t = legend_ax.text( left, top, str(my_text), horizontalalignment='left',
                           verticalalignment='top', size=prefs['text_size'])
        t.set_fontname( prefs['font'] )
        t.set_family( prefs['font_family'] )

      # Create legend rectangle:
        patch = Rectangle( ((column_width*(offset % prefs['columns']) + \
                        1.2*prefs['text_padding']/leg_pix_width),
                        top - box_width/leg_pix_height),
                        1.2*box_width/leg_pix_width, 1.2*box_width/leg_pix_height )
        patch.set_ec('black')
        patch.set_linewidth(0.25)
        patch.set_fc( my_color )
        legend_ax.add_patch( patch )
      offset += 1

    # Set some additional text if we stopped early
    if early_stop == True:
      my_text = '... plus %i more' % (num_labels - offset)
      if legend: legend_ax.text( left, top, my_text, horizontalalignment='left',
                    verticalalignment='top', size = prefs['text_size'] )

    top = 1 - column_height*( rows-1 )
    left = 0.5

    if bottom_text != None:
      if legend:
        t = legend_ax.text( left, top, str(bottom_text), horizontalalignment='center',
                      verticalalignment='top', size=prefs['text_size'] )
      t.set_family( prefs['font_family'] )
      t.set_fontname( prefs['font'] )

    formatter_cb( ax )
  
    self.ax = ax
    self.canvas = canvas
    self.fig = fig

  def write_graph( self ):
    kw = self.kw
    file = self.file
    canvas = self.canvas
    if 'svg' in kw.keys():
      svg = kw['svg']
    else:
      svg = False
    if isinstance( file , StringIO.StringIO ) or type(file) == cStringIO_type:
      canvas.draw() # **kw )
      if svg:
          renderer = RendererSVG(prefs[width], prefs[height], file)
          canvas.figure.draw(renderer)
          renderer.finish()
      else:
        size = canvas.get_renderer().get_canvas_width_height()
        buf=canvas.tostring_argb()
        im=PILImage.fromstring('RGBA', size, buf, 'raw', 'RGBA', 0, 1)

        # We must realign the color bands, as matplotlib outputs
        # ARGB and PIL uses RGBA.
        a, r, g, b = im.split()
        im = PILImage.merge( 'RGBA', (r, g, b, a) )
        im.save( file, format = 'PNG' ) 
    else: 
      canvas.print_figure(  file, **kw )

  def draw( self, **kw ):
    pass

class DBGraph( Graph ):

  def setup( self ):
    super( DBGraph, self ).setup()

    results = self.results; metadata = self.metadata
    kw = dict( self.kw )
    self.vars = metadata.get('sql_vars',{})
    self.title = getattr( self, 'title', find_info('title', kw, metadata ) )
    column_names = find_info( 'column_names', kw, metadata )
    column_units = find_info( 'column_units', kw, metadata )
    if len(str(column_units)) > 0:
      self.ylabel = "%s [%s]" % (column_names, column_units)
    else:
      self.ylabel = str(column_names)
    self.xlabel = find_info( 'grouping_name', kw, metadata )
    if len(self.xlabel) == 0:
      self.xlabel = find_info( 'xlabel', kw, metadata )
    self.kind  = find_info( 'pivot_name', kw, metadata )
    self.title = expand_string( self.title, self.vars )

class PivotGroupGraph( Graph ):

  def sort_keys( self, results ):
    if self.sorted_keys != None: return self.sorted_keys
    reverse_dict = {}
    for key, item in results.items():
      size = self.data_size( item )
      if size not in reverse_dict:
        reverse_dict[size] = [key]
      else:
        reverse_dict[size].append( key )
    sorted_dict_keys = reverse_dict.keys(); sorted_dict_keys.sort()
    sorted_dict_keys.reverse()
    sorted_keys = []
    for key in sorted_dict_keys:
      sorted_keys.extend( reverse_dict[key] )
    return sorted_keys

  def data_size( self, groups ):
    return max( groups.values() )

  def parse_pivot( self, pivot ):
    return pivot

  def parse_group( self, group ):
    return group

  def parse_datum( self, data ):
    return data

  def parse_data( self ):
    super( PivotGroupGraph, self ).parse_data()
    new_parsed_data = {}
    parsed_data = getattr( self, 'parsed_data', self.results )
    for pivot, groups in parsed_data.items():
      new_pivot = self.parse_pivot( pivot )
      new_groups = {}
      new_parsed_data[ new_pivot ] = new_groups
      for group, data in groups.items():
        new_group = self.parse_group( group )
        new_datum = self.parse_datum( data )
        new_groups[ new_group ] = new_datum
    self.parsed_data = new_parsed_data

class PivotGraph( Graph ):

  def sort_keys( self, results ):
    if self.sorted_keys != None: return self.sorted_keys
    reverse_dict = {}
    for key, item in results.items():
      size = self.data_size( item )
      if size not in reverse_dict:
        reverse_dict[size] = [key]
      else:
        reverse_dict[size].append( key )
    sorted_dict_keys = reverse_dict.keys(); sorted_dict_keys.sort()
    sorted_dict_keys.reverse()
    sorted_keys = []
    for key in sorted_dict_keys:
      sorted_keys.extend( reverse_dict[key] )
    return sorted_keys

  def data_size( self, item ): return abs(item)

  def parse_pivot( self, pivot ):
    return pivot
    
  def parse_datum( self, data ):
    return data
    
  def parse_data( self ):
    super( PivotGraph, self ).parse_data()
    new_parsed_data = {}
    parsed_data = getattr( self, 'parsed_data', self.results )
    for pivot, data in parsed_data.items():
      new_pivot = self.parse_pivot( pivot )
      new_parsed_data[ new_pivot ] = self.parse_datum( data )
    self.parsed_data = new_parsed_data

class TimeGraph( DBGraph ):

  def __init__( self, *args, **kw ):
    self.starttime_str = 'starttime'
    self.endtime_str = 'endtime'
    self.is_timestamps = True
    super( TimeGraph, self ).__init__( *args, **kw )

  def parse_group( self, group ):
    return to_timestamp( group )

  def formatter_cb( self, ax ): 
    ax.set_xlim( xmin=self.begin_num,xmax=self.end_num )
    dl = common.PrettyDateLocator()
    df = common.PrettyDateFormatter( dl )
    ax.xaxis.set_major_locator( dl )
    ax.xaxis.set_major_formatter( df )
    ax.xaxis.set_clip_on(False)
    sf = common.PrettyScalarFormatter( )
    ax.yaxis.set_major_formatter( sf )
    labels = ax.get_xticklabels()
  
  day_switch = 7
  week_switch = 7

  def add_time_to_title( self, title ):
    """ Given a title and two times, adds the time info to the title.
        Example results:
           "Number of Attempted Transfers\n(From 4:45 12-14-2006 to 5:56 12-15-2006)"
    """
    begin = self.begin; end  = self.end
    interval = self.time_interval( )
    if interval == 3600:
      format_str = '%Y-%m-%d %H:%M'
      format_name = 'Hours'
    elif interval == 86400:
      format_str = '%Y-%m-%d'
      format_name = 'Days'
    elif interval == 86400*7:
      format_str = '%Y/%U'
      format_name = 'Weeks'
    else:
      format_str = '%x %X'
      format_str = ''
    begin_tuple = time.gmtime(begin); end_tuple = time.gmtime(end)
    added_title = '\n%i %s from ' % (int((end-begin)/interval), format_name)
    added_title += time.strftime('%s to ' % format_str, begin_tuple)
    added_title += time.strftime(' %s UTC' % format_str, end_tuple)
    return title + added_title

  def time_interval( self ):
    begin = self.begin; end = self.end
    if end - begin < 86400*self.day_switch:
      return 3600
    elif end - begin < 86400*7*self.week_switch:
      return 86400
    else:
      return 86400*7

  def setup( self ):

    super( TimeGraph, self ).setup()

    vars = dict(self.vars)

    if 'croptime' in self.kw.keys():
      begin = numpy.inf; end = 0
      for pivot, groups in self.parsed_data.items():
        for timebin, data in groups.items():
          begin = min( timebin, begin )
          end = max( timebin, end )
    else:
      begin = to_timestamp(vars.get('starttime', time.time()-24*3600))
      end = to_timestamp(vars.get('endtime',time.time()))

    self.begin = begin; self.end = end
    self.begin_datetime = datetime.datetime.utcfromtimestamp( float(begin) )
    self.end_datetime   = datetime.datetime.utcfromtimestamp( float(end) )
    self.begin_num = date2num( self.begin_datetime )
    self.end_num   = date2num( self.end_datetime   )

    self.width = vars.get('span', self.time_interval() ) 

    title = getattr( self, 'title', '' )
    self.title = self.add_time_to_title( title )

  def write_graph( self ):
    if isinstance(self, PivotGroupGraph ) and self.ax != None:
      self.ax.set_xlim( xmin=self.begin_num, xmax=self.end_num )
    super( TimeGraph, self ).write_graph()

