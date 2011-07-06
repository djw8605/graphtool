#!/usr/bin/env python

#from setuptools import setup, find_packages
#from setuptools import find_packages
from distutils.core import setup

setup(
    name = "graphtool",
    version = "0.6.6",
    description = "CMS Common Graphing Package.",
    author = "Brian Bockelman",
    author_email = "bbockelm@math.unl.edu",
    packages = ['graphtool', 'graphtool.utilities', 'graphtool.tools', 'graphtool.base', 'graphtool.web', 'graphtool.graphs', 'graphtool.database', 'graphtool.static_content', 'graphtool.xml'],
    package_dir = {'graphtool.static_content': 'static_content', 'graphtool': 'src/graphtool'},
    package_data = {"graphtool.static_content":['*']},
    include_package_data = True,
    zip_safe = False,

    classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: POSIX'
    ],
    
    #dependency_links = ['http://effbot.org/downloads/Imaging-1.1.6.tar.gz#egg=PIL-1.1.6'],
    #install_requires=["CherryPy<=3.1", "matplotlib<=0.90.1", "numpy", "PIL"],
   
    entry_points={
        'console_scripts': [
            'graphtool = graphtool.utilities.graphtool_cli:main'
        ]
    },
 
)
