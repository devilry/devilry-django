# See the awsfabrictasks docs for more help:
# http://awsfabrictasks.readthedocs.org/en/latest/awsfab_settings.html

# Go to http://aws.amazon.com/, and select ``My account -> Security Credentials``
AUTH = {'aws_access_key_id': 'YOUR KEY HERE',
        'aws_secret_access_key': 'YOUR SECRET ACCESS KEY HERE'}


## Override keypair path if you do not keep your devilrydemo.pem in ``.`` or ``~/.ssh/``
#KEYPAIR_PATH = ['.', '~/.ssh/', '~/Dropbox/devilrykeys/']


## If you for some reason do not want to use ``devilrydemo.pem`` as your
## keypair, simply override it like this:
#from awsfab_settings import *   # NOTE: Put this at the top of this file, to ensure we do not override AUTH
#for config in EC2_LAUNCH_CONFIGS.itervalues():
    #config['key_name'] = 'mykey' # No .pem suffix
