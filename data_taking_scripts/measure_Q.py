from data_logging import DataLogger

auths_file = '/etc/rabbitmq-secret/authentications.json'
data_logger = DataLogger(auths_file)

center_freq = 17.81e9
span_freq = 100e6

start_freq = center_freq-span_freq/2
stop_freq = center_freq+span_freq/2

data_logger.log_transmission_switches(start_freq,stop_freq, 1, fitting = True, transmission_endpoint = 's21_iq_transmission_data')

data_logger.log_reflection_switches(start_freq, stop_freq, 1, fitting = True, reflection_endpoint = 's21_iq_reflection_data')
