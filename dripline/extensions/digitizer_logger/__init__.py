__all__ = []

import pkg_resources

import scarab
a_ver = '0.0.0' #note that this is updated in the following block
try:
    a_ver = pkg_resources.get_distribution('digitizer_logger_plugin').version
    print('version is: {}'.format(a_ver))
except:
    print('fail!')
    pass
version = scarab.VersionSemantic()
version.parse(a_ver)
version.package = 'digitizer_logger_plugin'
version.commit = '---'
__all__.append("version")

from .digitizer_logger import *
from .digitizer_logger import __all__ as __digitizer_logger_all
__all__ += __digitizer_logger_all

