
from graphtool.database.query_handler import QueryHandler
from graphtool.tools.common import expand_string, to_timestamp
from xml.sax.saxutils import XMLGenerator
import types, cStringIO, datetime, traceback

class ExtDict( dict ):
  pass

class QueryPrinter( QueryHandler ):
  """ Prints the results of a certain query.""" 

  def handle_query( self, results, *args, **kw ):
    out = cStringIO.StringIO()
    if len(results) > 0:
      #print >> out, "\nResults of query %s." % results.query.name
      print >> out, "\n", expand_string( results.query.title, results.sql_vars ).upper(), "\n"
      print >> out, "SQL USED:", str(results.query.sql)
      print >> out, "SQL VARS:"
      self.print_sql_vars( results, out )
      print >> out, "\n", "RESULTS:", '\n' 
    else:
      print >> out, "\nQuery has no results!\n"
    if results.kind == 'pivot-group':
      self.print_pivot_group_query( results, out )
    elif results.kind == 'pivot':
      self.print_pivot_query( results, out )
    else:
      print >> out, "\nUnknown query type!\n" 
    print out.getvalue()
    return out.getvalue()

  def print_sql_vars( self, results, out ):
    for var, val in results.sql_vars.items():
      print >> out, " - %s: %s" % (var, str(val))

  def print_pivot_group_query( self, results, out ):
    pivot_name = results.pivot_name
    units = []
    for unit in results.query.column_units.split(','):
      unit = unit.strip()
      units.append( unit )
    for pivot in results.keys():
      if len(results[pivot].keys()) > 0:
        first_item = results[pivot].values()[0]
        can_add = True; is_tuple = False
        if types.TupleType == type( first_item ):
          is_tuple = True 
          for result in first_item:
            if types.StringType == type(result): can_add = False
          cumulative_results = [0,] * len(first_item)
        else:
          if types.StringType == type( first_item ): can_add = False
          cumulative_results = 0
        if can_add == True: 
          for grouping in results[pivot].keys():
            if is_tuple:
              for idx in range(len(results[pivot][grouping])):
                cumulative_results[idx] += results[pivot][grouping][idx]
            else:
              cumulative_results += results[pivot][grouping] 
        if is_tuple:  
          print >> out, " * %s %s (Total: %s)\n" % (pivot_name, str(pivot), str(cumulative_results))
        else:
          print >> out, " * %s %s (Total: %.3f %s)\n" % (pivot_name, str(pivot), float(cumulative_results), units[0])
      if len(results[pivot].keys()) == 0 or can_add == False:
        print >> out, " * Pivot %s\n" % str(pivot)
      for grouping in results[pivot].keys():
        if is_tuple:
          print >> out, "   - %s: %s" % (grouping, results[pivot][grouping])
        else:
          print >> out, "   - %s: %.3f %s" % (grouping, float(results[pivot][grouping]), units[0])
      print >> out, ""

  def print_pivot_query( self, results, out ):
    pivot_name = results.pivot_name
    units = []; columns = []
    for unit in results.query.column_units.split(','):
      unit = unit.strip()
      units.append( unit )
    for column in results.query.column_names.split(','):
      columns.append( column.strip() )
    column_header_len = len(columns); column_units_len = len(units)
    for pivot, data in results.items():
      out.write( " * Pivot: %s, " % str(pivot) )
      if type(data) == types.TupleType:
        out.write( "\n" )
        for idx in range(len(data)):
          out.write( "   - " )
          if idx < column_header_len:
            out.write( "%s: " % columns[idx] )
          out.write( str(data[idx]) )
          if idx < column_units_len:
            out.write( " " + str(units[idx]) )
          out.write( "\n" )
      else:
        if column_header_len > 0:
          out.write( "%s: %s" % (columns[0], str(data)) )
        if column_units_len > 0:
          out.write( " " + units[0] )
        out.write( "\n" )
      out.write( "\n" )

  def handle_list( self, *args, **kw ):
    return self.list_queries()

class XmlGenerator( QueryHandler ):

  def handle_query( self, results, **kw ):
    query = results.query
    output = cStringIO.StringIO()
    gen = self.startPlot( output, results, query )
    if results.kind == 'pivot-group':
      self.addResults_pg( results, query, gen )
    elif results.kind == 'pivot':
      self.addResults_p( results, query, gen )
    elif results.kind == 'complex-pivot':
      self.addResults_c_p( results, query, gen )
    self.endPlot( gen )
    return output.getvalue()

  def handle_list( self, *args, **kw ):
    output = cStringIO.StringIO()
    gen = self.startDocument( output )
    base_url = ''
    if 'base_url' in self.__dict__:
      base_url = self.base_url
      if base_url[-1] != '/':
        base_url += '/'
    i = 0
    for query_obj in self.query_objs:
      i += 1
      if 'display_name' in query_obj.__dict__:
        name = query_obj.display_name
      else:
        name = "Query"
      gen.startElement("pagelist",{'name':name, 'id':str(i)})
      for page in query_obj.commands.keys():
        gen.characters("\t\t\n")
        attrs = {}
        my_page = self.known_commands[page]
        if 'title' in my_page.__dict__.keys():
          attrs['title'] = my_page.title
        gen.startElement('page',attrs)
        gen.characters( base_url + page )
        gen.endElement('page')
      gen.characters("\t\n")
      gen.endElement("pagelist")
      gen.characters("\t\n")
    self.endDocument( gen )
    return output.getvalue()

  def startDocument( self, output, encoding='UTF-8' ):
    gen =  XMLGenerator( output, encoding )
    gen.startDocument()
    output.write('<?xml-stylesheet type="text/xsl" href="/static/content/xml_results.xsl"?>\n')
    output.write('<!DOCTYPE graphtool-data>\n')
    gen.startElement('graphtool',{})
    gen.characters("\n\t")
    return gen

  def startPlot( self, output, results, query, encoding='UTF-8' ):
    gen = self.startDocument( output, encoding )
    query_attrs = {}
    name = query.name
    if name and len(name) > 0:
      query_attrs['name'] = name
    gen.startElement('query', query_attrs)
    gen.characters("\n\t\t")
    title = expand_string( query.title, results.sql_vars )
    if title and len(title) > 0:
      gen.startElement('title',{})
      gen.characters( title )
      gen.endElement( 'title' )
      gen.characters("\n\t\t")
    graph_type = query.graph_type
    if graph_type and len(graph_type) > 0:
      gen.startElement( 'graph',{} )
      gen.characters( graph_type )
      gen.endElement( 'graph' )
      gen.characters("\n\t\t")
    sql_string = str(query.sql)
    gen.startElement( 'sql',{} )
    gen.characters( sql_string )
    gen.characters("\n\t\t")
    gen.endElement( 'sql' )
    gen.characters("\n\t\t")
    self.write_sql_vars( results, query, gen )
    gen.characters("\n\t\t")
    base_url = '/graphs'
    try:
      if 'grapher' in query.self.__dict__.keys():
        graphs = query.self.grapher
      if 'base_url' in graphs.__dict__:
        base_url = graphs.base_url
    except Exception, e:
      pass
    self.write_graph_url( results, query, gen, base_url=base_url )
    return gen

  def write_graph_url( self, results, query, gen, base_url = '/graphs' ):
    base = base_url + '/' + query.name + '?'
    for key in results.given_kw.keys():
      base += str(key) + '=' + str(results.given_kw[key]) + '&'
    gen.startElement("url",{})
    gen.characters( base )
    gen.endElement("url")

  def write_sql_vars( self, data, query, gen ):
    sql_vars = data.sql_vars
    for key, item in data.given_kw.items():
      sql_vars[key] = item
    gen.startElement( 'sqlvars', {} )
    for var in sql_vars:
      gen.characters("\n\t\t\t")
      gen.startElement('var',{'name':var})
      gen.characters( str(sql_vars[var]) )
      gen.endElement('var')
    gen.characters("\n\t\t")
    gen.endElement( 'sqlvars' )
    gen.characters("\n\t\t")

  def endPlot( self, gen ):
    gen.endElement('query')
    gen.characters("\n")
    self.endDocument( gen )

  def endDocument( self, gen ):
    gen.endElement('graphtool')
    gen.characters("\n")
    gen.endDocument()

  def write_columns( self, query, gen ):
    names = [ i.strip() for i in query.column_names.split(',') ]
    units = [ i.strip() for i in query.column_units.split(',') ]
    columns = {}
    num_columns = min(len(names),len(units))
    for idx in range(num_columns):
      columns[names[idx]] = units[idx]
    if len(columns.items()) > 0:
      gen.startElement('columns',{})
      i=1
      for header in names:
        gen.characters("\n\t\t\t")
        gen.startElement('column',{'unit':columns[header], 'index':str(i)})
        i += 1
        gen.characters(header)
        gen.endElement('column')
      gen.characters("\n\t\t")
      gen.endElement('columns')
      gen.characters("\n\t\t")

  def addResults_pg( self, data, query, gen, **kw ):

    try:
      if 'grapher' in query.self.__dict__.keys():
        coords = query.self.grapher.get_coords( query, **data.given_kw )
      else: coords = None
    except Exception, e:
      #traceback.print_tb()
      coords = None

    attrs = {'kind':'pivot-group'}
    pivot_name = str(data.pivot_name)
    if pivot_name and len(pivot_name) > 0:
      attrs['pivot'] = pivot_name
    grouping_name = str(query.grouping_name)
    if grouping_name and len(grouping_name) > 0:
      attrs['group'] = grouping_name
    if coords:
      attrs['coords'] = 'True'
    else:
      attrs['coords'] = 'False'
    self.write_columns( query, gen )
    gen.startElement('data',attrs)

    for pivot in data.keys():
      gen.characters("\n\t\t\t")
      gen.startElement( *self.pivotName( pivot, attrs ) )
      my_groups = data[pivot].keys(); my_groups.sort(); my_groups.reverse()
      for grouping in my_groups:
        gen.characters("\n\t\t\t\t")
        grouping_attrs = {}
        gen.startElement('group', self.groupingAttrs( grouping_name, grouping ) )
        if coords:
          try:
            groups = coords[pivot]
            if type(grouping) == datetime.datetime and (not (grouping in groups.keys()) ):
              kw['coords'] = groups[to_timestamp(grouping)]
            else: kw['coords'] = groups[grouping] 
          except Exception, e:
            #print "Missing coords", pivot, grouping
            #print e
            pass
        self.addData( data[pivot][grouping], gen, **kw )
        gen.endElement('group')
      gen.endElement( self.pivotName( pivot, attrs )[0] )
    gen.characters("\n\t\t")
    gen.endElement('data')
    gen.characters("\n\t")

  def addResults_p( self, data, query, gen, **kw ):

    try:
      coords = query.self.grapher.get_coords( query, **data.given_kw )
    except Exception, e:
      #print e
      coords = None

    attrs = {'kind':'pivot'}
    pivot_name = str(data.pivot_name)
    if pivot_name and len(pivot_name) > 0:
      attrs['pivot'] = pivot_name
    if coords:
      attrs['coords'] = 'True'
    else:
      attrs['coords'] = 'False'

    self.write_columns( query, gen )
    gen.startElement('data',attrs)
    for pivot in data.keys():
      gen.characters("\n\t\t\t")
      gen.startElement( *self.pivotName(pivot, attrs) )
      if coords and (pivot in coords.keys()):
        kw['coords'] = coords[pivot]
      self.addData( data[pivot], gen, **kw )
      gen.characters("\n\t\t\t")
      gen.endElement( self.pivotName( pivot, attrs)[0] )
    gen.characters("\n\t\t")
    gen.endElement('data')
    gen.characters("\n\t")

  def addResults_c_p( self, data, query, gen, **kw ):
    attrs = {'kind':'pivot'}
    pivot_name = str(data.pivot_name)
    if pivot_name and len(pivot_name) > 0:
      attrs['pivot'] = pivot_name
    self.write_columns( query, gen )
    gen.startElement('data',attrs)
    for pivot, info in data:
      gen.characters("\n\t\t\t")
      gen.startElement( *self.pivotName(pivot, attrs) )
      self.addData( info, gen, **kw )
      gen.characters("\n\t\t\t")
      gen.endElement( self.pivotName( pivot, attrs)[0] )
    gen.characters("\n\t\t")
    gen.endElement('data')
    gen.characters("\n\t")    

  def groupingAttrs( self, grouping_name, grouping ):
    grouping_attrs = {}
    if grouping_name and grouping_name.lower()=='time':
      grouping_attrs['value'] = str(datetime.datetime.utcfromtimestamp(to_timestamp(grouping)))
    else:
      grouping_attrs['value'] = str(grouping)
    return grouping_attrs

  def pivotName( self, pivot, attrs ):
    if attrs['pivot'] == 'Link':
      return 'link', {'from':pivot[0],'to':pivot[1]}
    else:
      return attrs['pivot'].lower().strip(),{'name':str(pivot)}

  def addData( self, data, gen, coords=None, **kw ):
        if type(data) != types.TupleType:
          my_data = [  data ]
        else:
          my_data = data
        if coords:
          gen.characters("\n\t\t\t\t\t")
          coords = str( coords ).replace('(','').replace(')','')
          gen.startElement( 'coords', {} )
          gen.characters( coords )
          gen.endElement( 'coords' )
        for datum in my_data:
          gen.characters("\n\t\t\t\t\t")
          gen.startElement('d',{})
          gen.characters( str(datum) )
          gen.endElement( 'd' )
        gen.characters("\n\t\t\t\t")

