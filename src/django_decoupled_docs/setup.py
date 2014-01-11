from os.path import join, dirname
from setuptools import setup, find_packages

this_dir = dirname(__file__)

setup(name = 'django_decoupled_docs',
      description = 'A Django app that lets you decouple and translatable docs for your website/webapp.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools', 'Django'],
      include_package_data=True,
      long_description = open(join(this_dir, 'README.rst')).read().strip(),
      zip_safe=False,
      classifiers=[
                   'Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'
                  ]
)
