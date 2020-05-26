import random
import sys

from dripline.core.calibrate import calibrate
from dripline.implementations import KeyValueStore
__all__ = []

__all__.append("EntitiesSnapshotter")
class EntitiesSnapshotter(Entities, Interface):
    '''
    An entity that tells a list of entities to log themselves.
    '''

    def __init__(self, list_of_entities = [], **kwargs):
        '''
        Args:
            jitter_fraction (number): scaling factor for the random jitter factor
            seed (int||None): value to use to seed the PRNG
        '''
        # TODO throw error if list_of_entities is empty or contains an element that is not an entity.
        Entity.__init__(self, **kwargs)
        Interface.__init__(self, **kwargs)
        self._list_of_entities = list_of_entities
    def log_entities(self, _list_of_entities):
        for entity in _list_of_entities):
            self.cmd(entity, "scheduled_log")

