############################################################
:mod:`devilry_ziputil` --- Devilry utils models and backends
############################################################

The ``devilry_ziputil`` handles the creation of compressed archives.


*****************************
About the devilry ziputil app
*****************************
The ``devilry_ziputil`` app provides utilities for creating and adding archives using
``ZipUtil``, by providing a backend and a registry for the specialized backends to use.

``devilry_ziputil`` also provides a meta class used for caching that should be used to save
a entry in the database with info for locating a archived file in a backend.

By backend, we mean regular django file serving or a service that provides remote storage of
files such as f.ex: Amazon s3 or Heroku.


***********************
How to define a backend
***********************
First off, to define a backend, the URL to the storage location must be set in the Django settings config.
This should be done in the app the backend is used.

TODO!

**************************************************
Datamodel API for caching metainfo about a archive
**************************************************

.. py:currentmodule:: devilry.devilry_ziputil.models

.. automodule:: devilry.devilry_ziputil.models
    :members:

