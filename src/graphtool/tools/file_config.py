
#from graphtool.database import DatabaseInfo
from graphtool.base import GraphToolInfo
import os, readline

class FileConfig( GraphToolInfo ):
  """ This class allows one to determine proper defaults for the phedex-info
      command; it saves these defaults in the file ~/.phedexcfg.  
  """

  def __init__( self, *args, **kw ):
    super( FileConfig, self ).__init__( *args, **kw )
    config = self.get_config( ignore_error=True )
    for attr in config.keys():
      setattr( self, attr, config[attr] )

  commands = { 'default':'make_configuration',
               'set'    :'update_configuration',
               'get'    :'get_configuration'  }

  is_executable = True

  display_name = 'config' 

  def expand_path( self, path ):
    #return os.path.abspath( os.path.expandvars( os.path.expanduser( path ) ) )
    return os.path.expandvars( os.path.expanduser( path ) )

  def parse_path( self, path ):
    path = self.expand_path( path )
    dirname = os.path.dirname( path )
    basename = os.path.basename( path )
    allnames = os.listdir( dirname )
    allnames = [ i for i in allnames if i.startswith( basename ) ]
    retVals = []
    for i in allnames:
      if os.path.isdir( dirname + '/' + i ):
        retVals.append( i + '/' )
      else:
        retVals.append( i )
    return retVals

  def parse_dbparam_file( self, file, begin  ):
    f = open( file, 'r' )
    lines = f.readlines()
    f.close()
    lines = [ i for i in lines if (not i.strip().startswith('#')) ]
    sections = [ i.split()[1].strip() for i in lines if i.startswith('Section') ]
    sections = [ i for i in sections if i.startswith( begin ) ]
    return sections

  def file_complete( self, path, state ):
    if state == 0:
      self.possibilities = self.parse_path( readline.get_line_buffer() )
    if len(self.possibilities) > state:
      return self.possibilities[ state ]
    return None

  def dbparam_complete( self, file ):
    def complete( path, state ):
      buffer = readline.get_line_buffer()
      if state == 0:
        self.possibilities = self.parse_dbparam_file( file, buffer )
      if len(self.possibilities) > state:
        if self.possibilities[ state ] == buffer and len(self.possibilities) == 1:
          return None
        if len(buffer.split('/')) > 1:
          output = self.possibilities[ state ].split('/')[-1]
        else:
          output = self.possibilities[ state ]
        return output
      return None
    return complete

  def make_completer( self, options ):
    def complete( path, state ):
      buffer = readline.get_line_buffer()
      if state == 0:
        self.possibilities = [ i for i in options if i.startswith( buffer ) ]
      if len(self.possibilities) > state:
        if self.possibilities[ state ] == buffer and len(self.possibilities) == 1:
          return None
        if len(buffer.split('/')) > 1:
          output = self.possibilities[ state ].split('/')[-1]
        else:
          output = self.possibilities[ state ]
        return output
      return None
    return complete

  def fancy_input( self, strng, completer ):
    old_completer = readline.get_completer()
    readline.parse_and_bind("Tab: complete")
    readline.set_completer( completer )
    user_input = raw_input( strng )
    readline.set_completer( old_completer )
    return user_input

  def open_config( self, mode='r', ignore_error = False):
    try:
      home = os.environ['HOME']
      f = open(home + '/.phedexcfg', mode)
    except Exception, e:
      if ignore_error:
        return None
      else:
        print "Unable to open ~/.phedexcfg for editing."
        sys.exit(-1)
    return f

  def get_config( self, ignore_error=True ):
    f = self.open_config( ignore_error=ignore_error )
    config = {}
    if f == None:
      return config
    for line in f.readlines():
      attr, val = line.split('=')
      config[attr] = val.strip()
    return  config

  def write_config( self, config ):
    f = self.open_config( 'w' )
    for attr in config.keys():
      val = config[attr]
      val = val.strip()
      f.write( attr + '=' + val + '\n' )
    f.close()

  def make_configuration( self, *args, **kw ):
    """
    Asks interactive questions to determine correct defaults.
    """
    print "Please fill in the following info to configure the Phedex info tool."
    print "Tab completion is available for all inputs."
    config = self.get_config( )

    storage_file = ''
    while not os.path.exists( storage_file ):
      if storage_file != '':
        print "File does not exist - please try again."
      storage_file = self.fancy_input("Full path to the storage.xml file: ", self.file_complete )
      storage_file = self.expand_path( storage_file )
    config['storage'] = storage_file

    config_file = ''
    while not os.path.exists( config_file ):
      if config_file != '':
        print "File does not exist - please try again."
      config_file = self.fancy_input("Full path to XML config file: ", self.file_complete )
      config_file = self.expand_path( config_file )
    config['xml_config'] = config_file

    DBParam_file = ''
    while not os.path.exists( DBParam_file ):
      if DBParam_file != '':
        print "File does not exist - please try again."
      DBParam_file = self.fancy_input("DBParam file (e.g, /home/phedex4/protected/DBParam): ", self.file_complete )
      DBParam_file = self.expand_path( DBParam_file )

    DBParam_section = self.fancy_input("DBParam section (e.g., Prod/NEBRASKA): ", self.dbparam_complete( DBParam_file ) )

    config['db'] = DBParam_file + ':' + DBParam_section

    # Try and connect to the DB:
    print "Trying to connect to the DB with the above options (may take a few seconds)."
    try:
      my_db = DatabaseInfo( db=DBParam_file + ':' + DBParam_section )
      print "Starting sample query."
      orcl = my_db.orcl
      curs = orcl.cursor()
      curs.arraysize = 180
      curs.execute( "select name from t_node" )
      options = [ i[0] for i in curs.fetchall() ]
      curs.close(); orcl.close()
      print "Success!"
    except Exception, e:
      print "Unable to connect to database using given information!"
      print "Exception information:"
      print e
      options = []

    config['node'] = self.fancy_input("Node name of the site (e.g., T2_Nebraska_Buffer): ", self.make_completer( options ) )
    if len(options) > 1 and (not (config['node'] in options) ):
      print "Warning: Node not registered in Phedex database!"
    config['to_node'] = config['node']
    config['from_node'] = '.*'
    self.write_config( config )


  def update_configuration( self, *args, **kw ):
    """
    Sets the default value of certain attribute. Syntax:
     phedex-info.py config set --<attribute>=<value>
    """
    if len(args) > 0:
      print "This command does not take any non-keyword arguments!"
      print "Try arguments of the form '--attribute=value' instead."
      sys.exit(-1)
    config = self.get_config( )
    for key in kw.keys():
      config[key] = kw[key]
    self.write_config( config )

  def get_configuration( self, *args, **kw ):
    """
    Returns the default configuration of an attribute.  Syntax:
     phedex-info.py config get <attribute>
    """
    if len(args) != 1:
      print "Must specify the configuration option to print."
    config = self.get_config()
    if args[0] in config.keys():
      print config[args[0]]
    else:
      print "Unable to find configuration option %s" % args[0]



