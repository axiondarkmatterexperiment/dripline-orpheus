from dripline.core import Entity, calibrate, ThrowReply
from dripline.implementations import SimpleSCPIEntity, EthernetSCPIService
import logging
logger = logging.getLogger(__name__)
import time
from .muxer_calibrations import pt100_cal

__all__ = []

__all__.append("MuxerService")
class MuxerService(EthernetSCPIService):
    '''
    Provider to interface with muxer
    '''

    def __init__(self, scan_interval=0,**kwargs):
        '''
        scan_interval (int): time between scans in seconds
        '''
        EthernetSCPIService.__init__(self,**kwargs)
        if scan_interval <= 0:
            raise ThrowReply("scan interval must be > 0")
            #raise exceptions.DriplineValueError("scan interval must be > 0")
        self.scan_interval = scan_interval

    def configure_scan(self, *args, **kwargs):
        '''
        loops over the service's internal list of endpoints and attempts to configure each, then configures and begins scan
        '''
        self.send(['ABOR;*CLS;*OPC?'])

        ch_scan_list = list()
        for child in self.endpoints:

            if not isinstance(self.endpoints[child], MuxerGetEntity):
                continue
            elif self.endpoints[child].conf_str:
                # check if the configuration command associated with the endpoint is valid.
                error_data = self.send([self.endpoints[child].conf_str+';*OPC?',\
                                        'SYST:ERR?'])
                if error_data != '1;+0,"No error"':
                    logger.critical('Error detected; cannot configure muxer')
                    raise ThrowReply('{} when attempting to configure endpoint named "{}"'.format(error_data,child))
            ch_scan_list.append(str(self.endpoints[child].ch_number))
            self.endpoints[child].log_interval = self.scan_interval

        scan_list_cmd = 'ROUT:SCAN (@{})'.format(','.join(ch_scan_list))
        self.send([scan_list_cmd+';*OPC?',\
                   'TRIG:SOUR TIM;*OPC?',\
                   'TRIG:COUN INF;*OPC?',\
                   'TRIG:TIM {};*OPC?'.format(self.scan_interval),\
                   'INIT;*ESE?'])

__all__.append("MuxerGetEntity")
class MuxerGetEntity(Entity):
    '''
    Entity for communication with muxer endpoints.  No set functionality.
    '''

    #TODO define conditional logging.
    def __init__(self,
                 ch_number,
                 conf_str=None,
                 **kwargs):
        '''
        ch_number (int): channel number for endpoint
        conf_str (str): used by MuxerProvider to configure endpoint scan
        '''
        if conf_str is None:
            raise ThrowReply('conf_str required for MuxerGetEntity endpoint {}, set to False to not configure'.format(self.name))
        self.get_str = "DATA:LAST? (@{})".format(ch_number)
        self.ch_number = ch_number
        self.conf_str = conf_str.format(ch_number)
        Entity.__init__(self, **kwargs)

    @calibrate([pt100_cal])
    def on_get(self):
        result = self.service.send_to_device([self.get_str.format(self.ch_number)])
        logger.debug('very raw is: {}'.format(result))
        return result.split()[0]

    def on_set(self, value):
        raise ThrowReply('setting not available for {}'.format(self.name))


