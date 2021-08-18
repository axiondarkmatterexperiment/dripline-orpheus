__all__ = []

import pkg_resources

import scarab
a_ver = '0.0.0' #note that this is updated in the following block
try:
    a_ver = pkg_resources.get_distribution('power_detector_plugin').version
    print('version is: {}'.format(a_ver))
except:
    print('fail!')
    pass
version = scarab.VersionSemantic()
version.parse(a_ver)
version.package = 'power_detector_plugin'
version.commit = '---'
__all__.append("version")

from .power_detector import *
from .power_detector import __all__ as __power_detector_all
__all__ += __power_detector_all

