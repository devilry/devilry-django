# NOTE: You HAVE TO create a local override and set AUTH (aws credentials). See:
#       http://awsfabrictasks.readthedocs.org/en/latest/awsfab_settings.html


# Default region and availability zone
DEFAULT_REGION = 'eu-west-1'
DEFAULT_AVAILABILITY_ZONE = 'a'



#############################################################################
# Self documenting map of AMIs
# - You are not required to use this, but it makes it easier to read
#   EC2_LAUNCH_CONFIGS.
#############################################################################
ami = {
    'ubuntu-12.04-lts-64bit': 'ami-e1e8d395'
}


EC2_LAUNCH_CONFIGS = {
    'default': {
        'description': 'Settings used when creating a Devilry demo instance',

        # Ami ID
        'ami': ami['ubuntu-12.04-lts-64bit'],

        # AWS instance type API name. One of:
        #    m1.small, m1.large, m1.xlarge, c1.medium, c1.xlarge, m2.xlarge,
        #    m2.2xlarge, m2.4xlarge, cc1.4xlarge, t1.micro
        # Instance types with API names are listed here:
        #    http://aws.amazon.com/ec2/instance-types/
        'instance_type': 't1.micro',

        # List of security groups
        'security_groups': ["default"],

        # Use the ``list_regions`` task to see all available regions
        'region': DEFAULT_REGION,

        # The name of the key pair to use for instances (See http://console.aws.amazon.com -> EC2 -> Key Pairs)
        'key_name': 'devilrydemo',

        # The availability zone in which to launch the instances. This is
        # automatically prefixed by ``region``.
        'availability_zone': DEFAULT_AVAILABILITY_ZONE,

        # Tags to add to the instances. You can use the ``ec2_*_tag`` tasks or
        # the management interface to manage tags. Special tags:
        #   - Name: Should not be in this dict. It is specified when launching
        #           an instance (needs to be unique for each instance).
        #   - awsfab-ssh-user: The ``awsfab`` tasks use this user to log into your instance.
        'tags': {
            'awsfab-ssh-user': 'ubuntu'
        }
    }
}
