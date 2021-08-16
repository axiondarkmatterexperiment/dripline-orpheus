from dripline.core import Entity, calibrate, ThrowReply
from dripline.implementations import SimpleSCPIEntity
import logging
from .power_detector_calibration import zx47_50_cal

logger = logging.getLogger(__name__)

__all__ = []

__all__.append("PowerDetectorEntity")
class PowerDetectorEntity(SimpleSCPIEntity):
    '''
    Entity with power detector calibration
    '''

    @calibrate([zx47_50_cal])
    def on_get(self):
        return self._value

    def on_set(self, value):
        raise ThrowReply('setting not available for {}'.format(self.name))


