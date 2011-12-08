from setuptools import setup, find_packages

setup(
    name = "devilry",
    version = "1.1",
    url = 'http://devilry.org',
    license = 'BSD',
    description = "A system for handling electronic deliveries.",
    author = 'The Devilry developers',
    packages = find_packages(),
    install_requires = ['setuptools', 'Django==1.3.1', 'Markdown>=2.0.3',
                        'Pygments==1.4', 'flup==1.0.2', 'PyYAML==3.10']
)
