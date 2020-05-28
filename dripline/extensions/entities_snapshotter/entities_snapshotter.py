from dripline.core import Entity, Interface
import logging
logger = logging.getLogger(__name__)

__all__ = []

__all__.append("EntitiesSnapshotter")
class EntitiesSnapshotter(Entity):
    '''
    An entity that tells a list of entities to log themselves.
    '''

    def __init__(self, list_of_entities = [], auth_file = None , **kwargs):
        '''
        Args:
            list_of_entities (number): List of entities that you want to command to log themselves.
        '''
        # TODO throw error if list_of_entities is empty or contains an element that is not an entity.
        # TODO throw error if auth_file is none

        Entity.__init__(self, **kwargs)
        self._list_of_entities = list_of_entities
        self._auth_file = auth_file

    def log_entities(self):
        cmd_interface = Interface(dripline_config={'auth-file': self._auth_file})
        for entity in self._list_of_entities:
            logger.info(entity)
            cmd_interface.cmd(entity, "scheduled_log")
            logger.info('done with cmd')


