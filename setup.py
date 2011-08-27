from setuptools import setup, find_packages

setup(
    name = "devilry",
    version = "1.1",
    url = 'http://devilry.org',
    license = 'BSD',
    description = "A system for handling electronic deliveries.",
    author = 'The Devilry developers',
    packages = find_packages(),
    install_requires = ['setuptools', 'Django==1.3', 'Markdown>=2.0.3']
)
