#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages


setup(name = 'devilry_xmlrpc_client',
    version = '0.1.6',
    description = 'The devilry xmlrpc client and shell scripts.',
    url = 'http://devilry.github.com',
    author = 'Devilry',
    author_email = 'devilry-support@ifi.uio.no',
    package_dir = {'devilry_xmlrpc_client': ''},
    packages = ['devilry_xmlrpc_client'],
    scripts = ['devilry-examiner.py']
)
