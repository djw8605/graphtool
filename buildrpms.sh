#!/bin/bash
python setup.py bdist_rpm 
cat changelog.txt >> build/bdist.linux-x86_64/rpm/SPECS/graphtool.spec
cd build/bdist.linux-x86_64/rpm/
rpmbuild --define "_topdir $PWD" -bs SPECS/graphtool.spec

