Install the selenium server
###########################

Download selenium RC from http://seleniumhq.org/download/. Put
``selenium-server.jar`` somewhere of your choice.


Install the selenium python library
###################################

Instructions here: http://pypi.python.org/pypi/selenium/2.0a5

Note that the instructions say to use ``pip install -U selenium``, but::

    ~$ easy_install -U selenium

Works as well.


Running the tests
#################

1. Start the selenium server with (from where you installed it)::

    ~$ java -jar selenium-server.jar

2. Start the django server (from this directory)::

    ~$ python manage.py runserver

3. Run the tests with::

    ~$ make selenium-tests
