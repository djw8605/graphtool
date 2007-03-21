
from graphtool.base import GraphToolInfo
from graphtool.tools.file_config import FileConfig
from xml.dom.minidom import parse
import types, traceback, cStringIO

class XmlConfig( FileConfig ):

  def __init__( self, *args, **kw ):
    super( XmlConfig, self ).__init__( *args, **kw )
    self.dom = None; self.file = None 
    self.consume_keyword( 'dom' )
    self.consume_keyword( 'file' )
    self.globals['_imported_files'] = []
    if self.dom:
      self.parse_dom()
    if self.file:
      self.parse_file()

  def parse_dom( self ):
    self.parse_attributes( self, self.dom )

  def parse_attributes( self, obj, dom ):
    is_dict = isinstance( obj, types.DictType )
    for child in dom.getElementsByTagName('attribute'):
      if not (child in dom.childNodes):
        continue
      name = child.getAttribute('name')
      value = child.firstChild
      if name == '': continue
      if value == None:
        value = ''
      elif value.nodeType != value.TEXT_NODE:
        continue
      else:
        value = str(value.data).strip()
      try:
        if is_dict:
          obj[ name ] = value
        else:
          setattr( obj, name, value )
      except Exception, e:
        raise Exception( "Unable to set attribute %s to value %s\n%s" % (name, value, str(e)) )

  def parse_file( self, file=None ):
    if file == None: file = self.file
    file = self.expand_path( file )

    # Make checks to insure we import each file once.
    if file in self.globals['_imported_files']:
      return None
    self.globals['_imported_files'].append( file )

    # Try to open the file.
    if type(file) == types.StringType or type(file) == types.UnicodeType:
      try:
        file = open( file, 'r' )
      except Exception, e:
        raise Exception( "The XML parser tried to open file named %s, but failed.  Check to make sure it exists and is readable.  Initial exception: %s" % (file,str(e)) )
    elif 'read' in file.__dict__.keys():
      pass
    else:
      raise Exception( "The XML parser was instructed to parse an object which does not look like a file or a filename; %s" % str(file) )

    dom = parse( file )
    dom = dom.getElementsByTagName('phedex')[0]
    for import_dom in dom.getElementsByTagName('import'):
      self.parse_import( import_dom )
    for class_dom in dom.getElementsByTagName('class'):
      self.parse_class( class_dom )

  def parse_import( self, dom ):
    file = dom.getAttribute('file')
    if file != '':
      try:
        XmlConfig( file=file )
      except Exception, e:
        st = cStringIO.StringIO()
        traceback.print_exc( file=st )
        raise Exception( "Error in parsing file %s:\n%s\n%s" % (file, str(e), st.getvalue()) )
    module_name = dom.getAttribute('module')
    if module_name != '':
      text_node = dom.firstChild
      module = import_module( module_name )
      if text_node != None and text_node.nodeType == text_node.TEXT_NODE: 
        text = str(text_node.data).strip()
        objnames = text.split(',')
        for objname in objnames:
          objname = objname.strip()
          if objname == '*':
            for name in module.__dict__:
              self.globals[name] = getattr(module,name)
          else:
            self.globals[objname] = getattr(module,objname)
      else:
        self.globals[module_name] = module

  def parse_class( self, dom ):
    class_name = dom.getAttribute('type')
    objname = dom.getAttribute('name')
    if objname in self.globals.keys(): return
    try:
      my_class = self.globals[class_name]
    except:
      raise  Exception("Could not load class %s.  Was it imported?" % class_name)
    #try:
    self.globals[objname] = my_class( dom=dom )
    #except Exception, e:
    #  print "\nUnable to load class", class_name
    #  print "Exception thrown:"
    #  print e, "\n"

def attributes_to_dict( attribute_dom ):
  attrs = {}
  for child in attribute_dom.getElementsByTagName('attribute'):
    name = child.getAttribute('name')
    value = child.firstChild
    if name == '': continue
    if value == None or value.nodeType != value.TEXT_NODE: continue
    attrs[name] = value
  return attrs

def import_module( module_name ):
  module_list = module_name.split('.')
  module = __import__( module_name )
  if len(module_list) > 1:
    for mod_name in module_list[1:]:
      try:
        module = getattr( module, mod_name )
      except AttributeError, ae:
        #print "Module %s has no submodule named %s" % (str(module), mod_name)
        raise ae
  return module


