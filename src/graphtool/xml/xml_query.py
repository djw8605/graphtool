
from graphtool.base.xml_config import XmlConfig 

class XmlQueries( XmlConfig ):

  def __init__( self, *args, **kw ):
    self.commands = {}
    super( XmlQueries, self ).__init__( *args, **kw )
    
  def parse_dom( self ):
    super( XmlQueries, self ).parse_dom()
    self.name = self.dom.getAttribute('name')
    for query in self.dom.getElementsByTagName('query'):
      if query not in self.dom.childNodes: continue
      self.parse_query( query )
    
  def parse_query( self, query_dom ):
    query_class_name = query_dom.getAttribute('class')
    if query_class_name == None or len(query_class_name) == 0:
      query_class_name = 'XmlQuery'
    
    query_class = self.globals[ query_class_name ]
    
    query_obj = query_class( query_dom, self )
    
    for kw, item in self.metadata.items():
      if kw not in query_obj.metadata:
        query_obj.metadata[kw] = item

    name = query_dom.getAttribute('name')
    setattr( self, name, query_obj )
    self.commands[name] = name

class XmlQuery( XmlConfig ):

  def __init__( self, query_dom, parent_obj ):
    self.queries_obj = parent_obj
    
  def __call__( self, *args, **kw ):  return self.query( *args, **kw )



