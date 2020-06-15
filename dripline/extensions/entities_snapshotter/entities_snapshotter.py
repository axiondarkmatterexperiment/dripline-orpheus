from dripline.core import Entity, Interface, ThrowReply, get_return_codes_dict
from dripline.implementations import KeyValueStore, SimpleSCPIEntity
import logging
logger = logging.getLogger(__name__)

__all__ = []

__all__.append("EntitiesSnapshotter")
class EntitiesSnapshotter(Entity):
    '''
    An entity that tells a list of entities to log themselves.
    '''
    # TODO define get, set behavior

    def __init__(self, list_of_entities = [], auths_file = None , **kwargs):
        '''
        Args:
            list_of_entities (number): List of entities that you want to command to log themselves.
        '''
        # TODO throw error if list_of_entities is empty or contains an element that is not an entity.
        # TODO throw error if auth_file is none

        Entity.__init__(self, **kwargs)
        self._list_of_entities = list_of_entities
        self._auths_file = auths_file

    def log_entities(self):
        cmd_interface = Interface(dripline_config={'auth-file': self._auths_file})
        for entity in self._list_of_entities:
            logger.info(entity)
            cmd_interface.cmd(entity, "scheduled_log")
            logger.info('done with cmd')

__all__.append("LimitedKeyValues")
class LimitedKeyValues(KeyValueStore):
    '''
    An entity that only accepts a limited range of values
    '''
    def __init__(self, allowed_values= [], **kwargs):
        '''
        Args:
            allowed_values: a list of values that the entity can accept
        '''

        KeyValueStore.__init__(self, **kwargs)
        if not allowed_values:
            raise ThrowReply('service_error_invalid_value', "Need to specify list of values to accept")
        self._allowed_values = allowed_values

    def on_set(self, value):
        print(self._allowed_values)
        if not value in self._allowed_values:
            raise ThrowReply('service_error_invalid_value', "Set value is not allowed")
        return super().on_set(value)
