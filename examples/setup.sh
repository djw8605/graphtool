
export CMS_ROOT=/opt/test-aptinstaller-slc4
export CMS_ARCH=slc4_ia32_gcc345
export GRAPHTOOL_ROOT=$CMS_ROOT/GraphTool
export GRAPHTOOL_USER_ROOT=$GRAPHTOOL_ROOT/examples
export CONFIG_ROOT=$GRAPHTOOL_USER_ROOT/config

export PYTHONPATH=$GRAPHTOOL_USER_ROOT/src:$GRAPHTOOL_ROOT/src:$PYTHONPATH
export PATH=$GRAPHTOOL_USER_ROOT/tools:$PATH

export TTFPATH=$CMS_ROOT/$CMS_ARCH/external/py2-matplotlib/0.87.7/lib/python2.4/site-packages/matplotlib/mpl-data

# TODO:  Investigate.  Exporting HOME is bound to cause confustion, but there can be strange errors otherwise...
export HOME=$CONFIG_ROOT
export MATPLOTLIBDATA=$HOME

if [ -f $CMS_ROOT/$CMS_ARCH/.aptinstaller/cmspath ]; then

source $CMS_ROOT/$CMS_ARCH/external/oracle/10.2.0.2/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/libpng/1.2.10/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/python/2.4.3/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/py2-cx-oracle/4.2/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/py2-matplotlib/0.87.7/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/py2-numpy/1.0.1/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/libjpg/6b/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/libtiff/3.8.2/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/external/py2-pil/1.1.6/etc/profile.d/init.sh
source $CMS_ROOT/$CMS_ARCH/cms/oracle-env/1.2/etc/profile.d/init.sh

fi

