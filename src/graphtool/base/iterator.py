
from graphtool.base.xml_config import XmlConfig
import sys, cStringIO

class ObjectIterator( XmlConfig ):

  commands = { 'default' : 'run',
               'run' : 'run',
               'list' : 'list' }

  is_executable = False

  default_accepts_any = True

  def __init__( self, *args, **kw ):
    self.known_commands = {}
    super( ObjectIterator, self ).__init__( *args, **kw )  

  def parse_dom( self ):
    super( ObjectIterator, self ).parse_dom()
    classes = self.find_classes( must_be_executable=False )
    for obj_dom in self.dom.getElementsByTagName('obj'):
      text_node = obj_dom.firstChild
      if text_node.nodeType != text_node.TEXT_NODE: continue
      text = str( text_node.data.strip() )
      if not (text in classes.keys()):
        #print "Object for %s not found" % text
        continue
      obj = classes[text]
      #print "Object for iterator", obj
      for pair in obj.commands.items():
        #print "Adding", pair
        self.known_commands[pair[0]] = getattr(obj, pair[1])

  def handle_results( results, **kw ):
    return results

  def handle_args( self, *args, **kw ):
    return args, kw

  def handle_list( self, *args, **kw ):
    return self.list( *args, **kw )

  def run( self, *args, **kw ):
    if len(args) == 0:
      return self.handle_list( *args, **kw )
    cmd_args = args[1:]
    cmd_name = args[0]
    if cmd_name in self.known_commands.keys():
      cmd_func = self.known_commands[ cmd_name ]
    else:
      raise Exception( "Command name %s not known" % cmd_name )
    cmd_args, kw = self.handle_args( *cmd_args, **kw )
    results = cmd_func( *cmd_args, **kw )
    return self.handle_results( results, **kw )

  def list( self, *args, **kw ):
    out = cStringIO.StringIO()
    if len(self.known_commands.keys()) == 0:
      print >> out, "\nNo queries known!\n"
    else:
      print >> out, "Currently available queries:"
      for query_name in self.known_commands.keys():
        print >> out, " - %s" % query_name
      print >> out, ""
    print out.getvalue()
    return out.getvalue()


