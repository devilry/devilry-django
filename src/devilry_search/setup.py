from setuptools import setup, find_packages


setup(name = 'devilry_search',
      description = 'Devilry search helpers.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools', 'Django',
                          'devilry',
                          'django-haystack',
                          'celery-haystack'
                          ],
      include_package_data=True,
      long_description = 'Django-haystack search for Devilry.',
      zip_safe=False,
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'
                  ]
)
