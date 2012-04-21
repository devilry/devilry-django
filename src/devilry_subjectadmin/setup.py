from os.path import join, dirname
from setuptools import setup, find_packages

this_dir = dirname(__file__)

setup(name = 'devilry_subjectadmin',
      description = 'Subject (course) administrator interface for Devilry.',
      version = '1.0',
      license='BSD',
      url = 'https://github.com/devilry/devilry_subjectadmin',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools', 'Django', 'devilry',
                          'django_seleniumhelpers'],
      include_package_data=True,
      long_description = open(join(this_dir, 'README.rst')).read().strip(),
      zip_safe=False,
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'
                  ]
)
