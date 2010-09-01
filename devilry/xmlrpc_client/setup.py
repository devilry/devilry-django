#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup


setup(name = 'devilry_xmlrpc_client',
      version = '0.1',
      description = 'The devilry xmlrpc client and shell scripts.',
      url = 'http://devilry.github.com',
      author = 'Espen Angell Kristiansen',
      author_email = 'espeak@ifi.uio.no',
      package_dir = {'devilry_xmlrpc_client': ''},
      packages = ['devilry_xmlrpc_client'],
      scripts = ['devilry-examiner.py']
     )
