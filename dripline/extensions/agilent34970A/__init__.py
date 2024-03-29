__all__ = []

import pkg_resources

import scarab
a_ver = '0.0.0' #note that this is updated in the following block
try:
    a_ver = pkg_resources.get_distribution('agilent34970A_plugin').version
    print('version is: {}'.format(a_ver))
except:
    print('fail!')
    pass
version = scarab.VersionSemantic()
version.parse(a_ver)
version.package = 'agilent34970A_plugin'
version.commit = '---'
__all__.append("version")

from .agilent34970A import *
from .agilent34970A import __all__ as __agilent34970A_all
__all__ += __agilent34970A_all

