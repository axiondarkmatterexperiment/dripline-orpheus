from dripline.core import Entity

__all__ = []

__all__.append("EntitiesSnapshotter")
class EntitiesSnapshotter(Entity):
    '''
    An entity that tells a list of entities to log themselves.
    '''

    def __init__(self, list_of_entities = [], **kwargs):
        '''
        Args:
            list_of_entities (number): List of entities that you want to command to log themselves.
        '''
        # TODO throw error if list_of_entities is empty or contains an element that is not an entity.
        Entity.__init__(self, **kwargs)
        Interface.__init__(self, **kwargs)
        self._list_of_entities = list_of_entities

    def log_entities(self, _list_of_entities):
        for entity in _list_of_entities:
            self.cmd(entity, "scheduled_log")

    def cmd(self, endpoint, method, ordered_args=[], keyed_args={}, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        method (string): specifier to add to the message, naming the method to execute
        arguments (dict): dictionary of arguments to the specified method
        '''
        payload = {'values': ordered_args}
        payload.update(keyed_args)
        reply_pkg = self._send_request( msgop=op_t.cmd, target=endpoint, specifier=method, payload=payload )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result
