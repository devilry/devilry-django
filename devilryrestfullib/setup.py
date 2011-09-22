import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(
      name = "devilryrestfullib",
      version = "0.1",
      url = 'http://devilry.org',
      license = 'BSD',
      description = "Devilry RESTful client library.",
      author = 'The Devilry developers',
      packages = ['devilryrestfullib', 'devilryrestfullib.examples'],
      package_dir = {'devilryrestfullib': ''},
      install_requires = ['setuptools'])
