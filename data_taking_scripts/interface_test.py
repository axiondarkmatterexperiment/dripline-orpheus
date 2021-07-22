import time

print('Waiting before importing dripline interface')
time.sleep(10) # I can ctrl-c here and it would exit the python script

print('Now importing dripline interface')
from dripline.core import Interface
print('Waiting after importing dripline interface')
time.sleep(10) # Python script does not exit if I ctrl-c here.

auths_file = '/etc/rabbitmq-secret/authentications.json'
test_interface = Interface(dripline_config={'auth-file': auths_file})

#waffles is a JitterEntity from the tutorials. JitterEntity is modified to have an extra function called 'wait_for_no_reason' that just sleeps until dripline moves on because it doesn't receive a response.
print('Telling waffles to wait for some time')
test_interface.cmd('waffles', 'wait_for_no_reason') # dripline process exits if I ctrl-c here. Then it moves onto the next part of the python script

print('Waiting after telling waffles to wait')
time.sleep(10) # Python script does not exit if I ctrl-c here.
