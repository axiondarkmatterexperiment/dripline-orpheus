from dripline.core import Interface

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})
print(test_interface.get('peaches'))
