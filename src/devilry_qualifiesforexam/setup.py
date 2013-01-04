from setuptools import setup, find_packages


setup(name = 'devilry_qualifiesforexam',
      description = 'Devilry app that enables admins to determine students that qualifies for final exams.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools',
                          'devilry',
                          'devilry_subjectadmin',
                          'devilry_header',
                          'devilry_theme',
                          'devilry_i18n',
                          'devilry_extjsextras',
                          'djangorestframework'],
      include_package_data=True,
      long_description = open('README.rst').read(),
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
