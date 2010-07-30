Needs robotframework:
easy_install robotframework

SeleniumLibrary (http://code.google.com/p/robotframework-seleniumlibrary/wiki)
hg clone https://robotframework-seleniumlibrary.googlecode.com/hg/ robotframework-seleniumlibrary
python setup.py install

To run tests:
robotframework-seleniumlibrary/demo$ python rundemo.py selenium start

devilry$ make selenium-test
