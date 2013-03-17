from setuptools import setup, find_packages


setup(name = 'devilry_qualifiesforexam_select',
      description = 'Devilry qualifiesforexam plugin that allows an admin to manually select who qualifies for final exams.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools', 'Django',
                          'devilry_qualifiesforexam',
                          'devilry_theme',
                          'devilry_header',
                          'devilry_extjsextras',
                          'django_seleniumhelpers',
                          'django_extjs4',
                          ],
      include_package_data=True,
      long_description = 'See the Devilry docs for more info.',
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
