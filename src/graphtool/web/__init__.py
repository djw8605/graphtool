
from graphtool.base.xml_config import XmlConfig
from graphtool.base.iterator import ObjectIterator
import cherrypy, os

class WebHost( XmlConfig ):
  
  def parse_dom( self ):
    super( WebHost, self ).parse_dom( )
    for mount in self.dom.getElementsByTagName('mount'):
      self.parse_mount( mount )
    classes = self.globals
    for instance_dom in self.dom.getElementsByTagName('instance'):
      if not ( instance_dom in self.dom.childNodes ):
        continue
      name = instance_dom.getAttribute("name")
      if name == '': continue
      instance = classes[ name ]
      cherrypy.tree.mount( instance, '/' + name )
    for config in self.dom.getElementsByTagName('config'):
      text = config.firstChild
      if text and text.nodeType == text.TEXT_NODE:
        filename = str(text.data).strip()
        filename =  self.expand_path( filename )
        self.load_config( filename )

  def parse_mount( self, mount_dom ):
    location = mount_dom.getAttribute('location')
    if (not location) or len(location) == 0:
      return
    content = mount_dom.getAttribute('content')
    if not (content and len(content) > 0): content = None
    classes = self.find_classes()
    for class_dom in mount_dom.getElementsByTagName('class'):
      instance = classes[class_dom.getAttribute('type')]( dom=class_dom )
    for instance_dom in mount_dom.getElementsByTagName('instance'):
      instance = classes[instance_dom.getAttribute('name')]
    self.mount_instance( instance, location, content )
    instance.metadata['base_url'] = location

  def wrap_function( self, func, content ):
    def content_func( *args, **kw ):
      results = func( *args, **kw )
      cherrypy.response.headers['Content-Type'] = str(content) 
      return results
    return content_func

  def mount_instance( self, instance, location, content=None ):
    class DummyObject:
      _cp_config = {}
    do = DummyObject()
    for command, func_name in instance.commands.items():
      try:
        func = getattr(instance, func_name)
        if content: func = self.wrap_function( func, content )
        setattr( do, command, func )
        func.__dict__['exposed'] = True
        #print "Adding function %s as %s" % (func_name, command)
      except Exception, e:
        raise e
    #print "Mounting instance %s at location %s" % (do, location)
    cherrypy.tree.mount( do, location )
 
  def load_config( self, file ):
    cherrypy.config.update( file )
 
class StaticContent( XmlConfig ):

  _cp_config = {} 

  def index( self ):
    return "No index here!"
  index.exposed = True

  def parse_dom( self ):
    super( StaticContent, self ).parse_dom()
    for directory_dom in self.dom.getElementsByTagName('directory'):
      name = directory_dom.getAttribute('name')
      if name == '': continue
      directory_name_dom = directory_dom.firstChild
      if not (directory_name_dom and directory_name_dom.nodeType == self.dom.TEXT_NODE):
        continue
      dir_name = str( directory_name_dom.data ).strip()
      dir_name = self.expand_path( dir_name )
      handler = cherrypy.tools.staticdir.handler( section=name, dir=dir_name, root=os.getcwd() )
      setattr( self, name, handler )


class HelloWorld(object):

  static = cherrypy.tools.staticdir.handler(section='static', root=os.getcwd(),
                                     dir='static_content')

  def __init__( self, *args, **kw ): pass

  def condor( self, *args, **kw ):
    r = os.popen( 'condor_q -xml' )
    lines = r.readlines()
    xml_string = ''
    found_header = False
    for line in lines:
      if line.startswith('--'):
        found_header = True
        continue
      if found_header:
        if line.startswith('<!DOCTYPE'):
          continue
        xml_string += line 
        if line.startswith('<?xml version'):
          xml_string += '<?xml-stylesheet type="text/xsl" href="/static/content/condor_results.xsl"?>\n'
    cherrypy.response.headers['Content-Type'] = 'text/xml'
    return xml_string

  condor.exposed = True

  def index(self):
     return "Hello World! (Test Case)"
  index.exposed = True

