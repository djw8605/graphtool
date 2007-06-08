
from graphtool.tools.common import to_timestamp
import threading, time

class Cache( object ):
 
  def __init__( self, *args, **kw ):
    super( Cache, self ).__init__( *args, **kw )
    self.cache = {}
    self.cache_sorted = []
    self.cache_lock = threading.Lock()
    self.progress_lock = threading.Lock()
    self.progress = {}
    self.max_cache_size = 100
    self.cache_expire = 300 # seconds
    self.cache_timestamps = {}

  def add_cache( self, hash_str, results ):
    self.cache_lock.acquire()

    try:
      if hash_str in self.cache_sorted:
        self.cache_sorted.remove(hash_str)
      self.cache_sorted.append( hash_str )
      self.cache[ hash_str ] = results

      if len(self.cache_sorted) > self.max_cache_size:
        oldest = self.cache_sorted.pop(0)
        del self.cache[ oldest ]
        del self.cache_timestamps[ oldest ]

      self.cache_timestamps[ hash_str ] = time.time()

    finally:
      self.cache_lock.release()

  def check_cache( self, hash_str ):
    self.cache_lock.acquire()
    try:
      if (hash_str in self.cache_sorted) and (time.time() < self.cache_timestamps[hash_str] + self.cache_expire):
        results = self.cache[ hash_str ]
      else:
        results = None
    finally:
      self.cache_lock.release()
    return results

  def make_hash_str( self, query, **kw ):
    if 'starttime' in kw.keys():
      kw['starttime'] = int(to_timestamp(kw['starttime']))
    if 'endtime' in kw.keys():
      kw['endtime'] = int(to_timestamp(kw['endtime']))
    if 'starttime' in kw and 'endtime' in kw:
      if kw['endtime'] - kw['starttime'] > 300:
        kw['endtime'] -= kw['endtime'] % 10
        kw['starttime'] -= kw['starttime'] % 10
    hash_str = str(query)
    keys = kw.keys(); keys.sort()
    for key in keys:
      hash_str += ',' + str(key) + ',' + str(kw[key])
    return hash_str

  def add_progress( self, hash_str, get_lock=True ):
    if get_lock: self.progress_lock.acquire()
    new_lock = threading.Lock()
    new_lock.acquire()
    self.progress[ hash_str ] = new_lock
    if get_lock: self.progress_lock.release()


  def check_and_add_progress( self, hash_str ):
    self.progress_lock.acquire()
    if hash_str in self.progress.keys():
      results = self.progress[ hash_str ]
    else:
      self.add_progress( hash_str, False )
      results = None
    self.progress_lock.release()
    return results

  def remove_progress( self, hash_str ):
    self.progress_lock.acquire()
    lock = self.progress[ hash_str ]
    lock.release()
    del self.progress[ hash_str ]
    self.progress_lock.release()

  def cached_function(self, function, args, kwargs):
        hash_str = self.make_hash_str( graphName, args, **kwargs )

        graphing_lock = self.check_and_add_progress( hash_str )
    
        if graphing_lock:
            graphing_lock.acquire()
            results = self.check_cache( hash_str )
            graphing_lock.release()
            return results
        else:
            results =  self.check_cache( hash_str )
        if results:
            self.remove_progress( hash_str )
            return results
        try:
            results = function(*args, **kwargs)
        except Exception, e:
            self.remove_progress( hash_str )
            st = cStringIO.StringIO()
            traceback.print_exc( file=st )
            raise Exception( "Error in creating graph, hash_str:%s\n%s\n%s" % (hash_str, str(e), st.getvalue()) )
        self.add_cache( hash_str, (graph_results, file.getvalue()) )
        self.remove_progress( hash_str )
        return results
