from setuptools import setup, find_packages


setup(name = 'devilry_developer',
      description = 'Helpers and default settings for development of devilry.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools', 'Django',
                          'devilry', 'devilry_theme',
                          'devilry_header',
                          'devilry_extjsextras',
                          'django_seleniumhelpers', 'django_extjs4',
                          'devilry_examiner',
                          ],
      include_package_data=True,
      long_description = open('README.rst').read(),
      entry_points = {
          'zc.buildout': [
              'settingsfile = devilry_developer.buildoutrecipes:DevSettingFile',
              'staticfile = devilry_developer.buildoutrecipes:StaticFile',
              ]
          },
      zip_safe=False,
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: JavaScript',
                   'Programming Language :: Python'
                  ]
)
