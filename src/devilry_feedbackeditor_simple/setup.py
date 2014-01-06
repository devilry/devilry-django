from setuptools import setup, find_packages


setup(name = 'devilry_feedbackeditor_simple',
      description = 'Devilry app that implements the feedback editor interface.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = [
          'setuptools',
      ],
      include_package_data=True,
      long_description = 'Feedback editor interface proof of concept and example.',
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
