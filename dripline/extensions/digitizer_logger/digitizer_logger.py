from dripline.core import Interface, ThrowReply, get_return_codes_dict
from dripline.implementations import PostgresSensorLogger
import logging
logger = logging.getLogger(__name__)
import time

__all__ = []

__all__.append("PostgresDigitizerLogger")
class PostgresDigitizerLogger(PostgresSensorLogger):
    '''
    Postgres logger for the digitizer service
    '''
    def __init__(self, integrated_power_endpoint, **kwargs):
        '''
        '''
        PostgresSensorLogger.__init__(self,**kwargs)
        self._integrated_power_endpoint = integrated_power_endpoint
        self._python_interface = Interface(dripline_config={'auth-file': self._auths_file})

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        this_data_table = self.sync_children[self.insertion_table_endpoint_name]
        # combine data sources
        insert_data = {'timestamp': a_message_timestamp}
        insert_data.update(a_routing_key_data)
        print(a_routing_key_data)
        insert_data.update(a_payload.to_python())
        logger.info(f"insert data are:\n{insert_data}")
        if a_routing_key_data == 'fast_daq.medium_spectrum':
            calculated_integrated_power = np.sum(insert_data['value_raw'])
            self._python_interface.set(self._integrated_power_endpoint, calculated_integrated_power)
            self._python_interface.cdm(self._integrated_power_endpoint, "scheduled_log")
        # do the insert
        this_data_table.do_insert(**insert_data)
        logger.info("finished processing data")

