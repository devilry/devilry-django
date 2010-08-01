.. _developer-selenium-tests:

================================================
Selenium tests
================================================

Requirements for Selenium testing
#######################################################################


**robotframework** (http://code.google.com/p/robotframework/wiki/)

Install::

 $ easy_install robotframework

**SeleniumLibrary** (http://code.google.com/p/robotframework-seleniumlibrary/wiki)

Install::

 $ hg clone https://robotframework-seleniumlibrary.googlecode.com/hg/ robotframework-seleniumlibrary
 $ python setup.py install

Running the tests
########################################################################

To run tests, first start the selenium server ::

 robotframework-seleniumlibrary/demo$ python rundemo.py selenium start

Then run the tests with::

 devilry$ make selenium-test

The server is stopped with::

 robotframework-seleniumlibrary/demo$ python rundemo.py selenium stop

Creating Selenium tests using Firefox plugin
########################################################################

To create tests through Firefox using Firefox pugin, install Selenium IDE:
http://seleniumhq.org/download/

**Creating the python test**

- Go to Tools->Selenium IDE in Firefox
- Go to the web page you wish to record.
- To the operations you want to test.
- To finish recording, click the record button.
- To get the python code, go to Options->Format and choose Python.
