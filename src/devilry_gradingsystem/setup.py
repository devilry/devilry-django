from setuptools import setup, find_packages


setup(name = 'devilry_gradingsystem',
      description = 'Devilry app that provides the grading system plugin framework.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = [
          'setuptools',
      ],
      include_package_data=True,
      long_description = 'Grading system plugin framework, base classes, base templates, etc.',
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
