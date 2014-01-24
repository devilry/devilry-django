from setuptools import setup, find_packages


setup(name = 'devilry_settings',
      description = 'Devilry settings.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = [
            'setuptools',
            'devilry',
            'devilry_examiner',
            'devilry_gradingsystem',
            'devilry_gradingsystemplugin_points',
            'devilry_gradingsystemplugin_approved',
            'django_decoupled_docs',
      ],
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
