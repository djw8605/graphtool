#!/usr/bin/env python

from distutils.core import setup

setup(
  name = "graphtool",
  version = "0.3",
  description = "Common Graphing Package.",
  author = "Brian Bockelman",
  author_email = "bbockelm@math.unl.edu",
  package_dir = {'' : 'src'},
  packages = ['graphtool','graphtool.base','graphtool.graphs','graphtool.tools','graphtool.web', 'graphtool.database'],
)
