from setuptools import setup, find_packages


setup(
    name = 'devilry_calendar',
    description = 'Devilry Calendar overview of important events',
    version = '1.0',
    license='BSD',
    author = 'Tor Ivar Johansen',
    packages=find_packages(exclude=['ez_setup']),
    install_requires = [
        'setuptools', 'Django',
        'devilry',
        ],
    include_package_data=True,
    long_description = 'Devilry Calendar overview of important events.',
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
