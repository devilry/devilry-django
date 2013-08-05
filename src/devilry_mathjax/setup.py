from setuptools import setup, find_packages


setup(name = 'devilry_mathjax',
      description = 'MathJaX bundled for Devilry.',
      version = '1.0',
      license='BSD',
      author = 'Espen Angell Kristiansen and Tor Ivar Johansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['setuptools', 'Django'],
      include_package_data=True,
      long_description = 'TODO',
      zip_safe=False,
      classifiers=[
                   'Development Status :: 5 - Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'
                  ]
)
