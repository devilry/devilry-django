import json
from setuptools import setup, find_packages


with open('devilry/version.json') as versionfile:
    version = json.load(versionfile)


setup(
    name="devilry",
    version=version,
    url='http://devilry.org',
    license='BSD',
    description="A system for handling electronic deliveries.",
    author='The Devilry developers',
    packages=find_packages(),
    install_requires=['setuptools']
)
