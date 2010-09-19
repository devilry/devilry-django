.. _developer-selenium-tests:

================================================
Selenium tests
================================================

Requirements for Selenium testing
#######################################################################

Install the selenium server
---------------------------

Download *Selenium RC* from http://seleniumhq.org/. Put
``selenium-server.jar`` somewhere of your choice. At the time of writing, the
.jar-file is in ``selenium-server-VERSION/``.


Install the selenium python library
-----------------------------------

Two alternatives:

1. Install from pypi:

    Instructions here: http://pypi.python.org/pypi/selenium/

    Note that the instructions say to use ``pip install -U selenium``, but::

        ~$ easy_install -U selenium

    Works as well.

2. Install from source:

    The selenium python library is a single python file, ``selenium.py``, that
    you need to add to you PYTHONPATH. At the time of writing it is located in
    ``selenium-python-client-driver-VERSION/`` in the Selenium RC package you
    downloaded to install the selenium server.


Running the tests
########################################################################

1. Start the selenium server with (from where you installed it)::

    ~$ java -jar selenium-server.jar

2. Start the django server (from this directory)::

    ~$ python manage.py runserver

3. Run the tests with::

    ~$ make selenium-tests


Creating Selenium tests using Firefox plugin
########################################################################

To create tests through Firefox using Firefox pugin, install 
`Selenium IDE <http://seleniumhq.org/download/>`_:

To create the python test using the selenium firefox plugin:

- Go to Tools->Selenium IDE in Firefox
- Go to the web page you wish to record.
- To the operations you want to test.
- To finish recording, click the record button.
- To get the python code, go to Options->Format and choose Python.
