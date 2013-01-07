from os.path import join, dirname
from setuptools import setup, find_packages

this_dir = dirname(__file__)

setup(
    name = 'devilry_nodeadmin',
    description = " ".join([ 
        'Node admins are the admins who have access to a huge amount', 
        'of subjects. They need a user interface where they can browse',
        'their departments (including subjects, semesters, assignments,',
        'students, ...).' ]),
    license = 'BSD',
    author = 'Ilya Kostolomov',
    packages = find_packages( exclude=['ez_setup'] ),
    install_requires = [ 
        'setuptools',
        'Django',
        'devilry',
        'devilry_theme',
        'devilry_usersearch',
        'devilry_extjsextras',
        'django_seleniumhelpers',
        'django_extjs4',
        'djangosenchatools',
        'djangorestframework'],
    include_package_data = True,
    long_description = open( join( this_dir, 'README.rst' ) ).read().strip(),
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Indended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
