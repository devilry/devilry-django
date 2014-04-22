from setuptools import setup, find_packages


setup(name = 'devilry_theme2',
      description = 'The devilry theme version 2.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=[]),
      install_requires = ['setuptools'],
      include_package_data=True,
      long_description = 'See http://devilry.org',
      zip_safe=False,
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent'
                  ]
)
