from dripline.core import Entity, calibrate, ThrowReply
from dripline.implementations import EthernetSCPIService
import logging
logger = logging.getLogger(__name__)
import time
from .muxer_calibrations import pt100_cal
from .muxer_calibrations import x83871_cal

__all__ = []

__all__.append("MuxerService")
class MuxerService(EthernetSCPIService):
    '''
    Provider to interface with muxer
    '''
    def configure_scan(self, *args, **kwargs):
        '''
        loops over the service's internal list of endpoints and attempts to configure each, then configures and begins scan
        '''
        self.send_to_device('ABOR;*CLS;*OPC?')

        ch_scan_list = list()
        logger.info(self.sync_children)
        logger.info(self)
        logger.info(self.__dict__)
        for child in self.sync_children:

            logger.info(child)
            if not isinstance(self.sync_children[child], MuxerGetEntity):
                logger.info(child)
                logger.info('help0')
                continue
            elif self.sync_children[child].conf_str:
                # check if the configuration command associated with the endpoint is valid.
                error_data = self.send(self.sync_children[child].conf_str+';*OPC?; SYST:ERR?')
                logger.info('help')
                if error_data != '1;+0,"No error"':
                    logger.critical('Error detected; cannot configure muxer')
                    raise ThrowReply('{} when attempting to configure endpoint named "{}"'.format(error_data,child))
                logger.info('help2')
            ch_scan_list.append(str(self.sync_children[child].ch_number))
            self.sync_children[child].log_interval = self.scan_interval

        logger.info('help3')
        scan_list_cmd = 'ROUT:SCAN (@{})'.format(','.join(ch_scan_list))
        logger.info('help4')
        self.send_to_device(scan_list_cmd+';*OPC?;'+\
                   'TRIG:SOUR TIM;*OPC?;'+\
                   'TRIG:COUN INF;*OPC?;'+\
                   'TRIG:TIM {};*OPC?;'.format(self.scan_interval)+\
                   'INIT;*ESE?;')


    def __init__(self, scan_interval=0,**kwargs):
        '''
        scan_interval (int): time between scans in seconds
        '''
        EthernetSCPIService.__init__(self,**kwargs)
        if scan_interval <= 0:
            raise ThrowReply("scan interval must be > 0")
            #raise exceptions.DriplineValueError("scan interval must be > 0")
        self.scan_interval = scan_interval

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
        if not result:
            raise ThrowReply("result from on_get is empty")
        logger.debug('very raw is: {}'.format(result))
        logger.info("Result in on_get:")
        return result.split()[0]

    def on_set(self, value):
        raise ThrowReply('setting not available for {}'.format(self.name))


