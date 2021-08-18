__all__ = []

import pkg_resources

import scarab
a_ver = '0.0.0' #note that this is updated in the following block
try:
    a_ver = pkg_resources.get_distribution('entities_snapshotter_plugin').version
    print('version is: {}'.format(a_ver))
except:
    print('fail!')
    pass
version = scarab.VersionSemantic()
version.parse(a_ver)
version.package = 'entities_snapshotter_plugin'
version.commit = '---'
__all__.append("version")

from .entities_snapshotter import *
from .entities_snapshotter import __all__ as __entities_snapshotter_all
__all__ += __entities_snapshotter_all

