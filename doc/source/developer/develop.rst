.. _developer-develop:

=================================
How to contribute code to Devilry
=================================

1. Fork the `devilry sourcecode`_ using the fork-button on github.
2. Make changes to your fork
3. Make sure you fork is fully merged with the `devilry sourcecode`_.
4. Send a pull request to *espeak* and *bendikro* using the pull request button
   *on your fork*.

If we consider your code stable and useful enough, we will merge it into the
devilry sourcecode. It is important to understand that we might not accept your
code (for various) reasons, so you should probably message us your idea before
you start coding. You should also be prepared to have to go a couple of rounds
of reviews before we accept your code, especially if it is a big change.


Source code guidelines
======================

We follow the official python guidelines for python code (`PEP 8`_). Additional
restrictions:
    - Use spaces-only for indentation.
    - Write `tests`_ (selenium-tests for webinterfaces). We do not accept new
      code into the tree without tests.
    - Write ref:`documentation <documentation>`. We prefer a howto/examples in
      addition to API-docs (see :ref:`grade-plugins` for a example.)

.. _`devilry sourcecode`: http://github.com/devilry/devilry-django/tree/master/devilry/
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/
.. _tests: http://docs.djangoproject.com/en/dev/topics/testing/
