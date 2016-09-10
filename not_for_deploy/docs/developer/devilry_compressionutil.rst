####################################################################
:mod:`devilry_compressionutil` --- Devilry utils models and backends
####################################################################

The ``devilry_compressionutil`` handles the creation of compressed archives.


*************************************
About the devilry compressionutil app
*************************************
The ``devilry_compressionutil`` app provides utilities for creating and adding archives using
``ZipUtil``, by providing a backend and a registry for the specialized backends to use.

``devilry_compressionutil`` also provides a meta class used for caching metainfo about a archive.


***********************
How to define a backend
***********************

**Add path setting**

First off, add a path to the storage location Django settings config.
Call this setting ``DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY``

.. code-block:: python

   DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY = os.path.join('path', 'to', 'storage', 'location')


**Subclass backend**

Create a backend for your app that you will use to compress the files by subclassing e.g
``PythonZipFileBackend`` in ``devilry.devilry_compressionutil.backends.backends_base``.

.. code-block:: python

   from devilry.devilry_compressionutil.backends import backends_base

   class YourAppZipBackend(backends_base.PythonZipFileBackend):
       backend_id = 'some_backend_id'

       def __init__(self, **kwargs):
           super(YourAppZipBackend, self).__init__(**kwargs)
           # Create path to archive storage if it does not exist.

**Load backend to registry**

Create an AppConfig for your app.
Load the backend you created to the ``devilry_compressionutil`` s registry.
Here you can register as many backends as you want, and just fetch it by its ``backend_id``.
The registry is a singleton, and to add a backend to it ``Registry.get_instance().add(..)`` must be called.

.. code-block:: python

   ...
   from devilry.devilry_compressionutil import backend_registry

   class YourAppAppConfig(AppConfig):
       ...

       def ready(self):
           from devilry.your_app import your_backends
           backend_registry.Registry.get_instance().add(your_backends.YourAppZipBackend)


**Get backend and add folders and files to it**

Add paths and files to the backend.

.. code-block:: python

   from devilry.devilry_compressionutil import backend_registry

   class HandleZipping:
       ...

       def your_function_that_uses_zip_backend(...):
           backend_class = backend_registry.Registry.get_instance().get('some_backend_id')

           # Path to archive inside the location specified by the storage location defined in
           # settings. ``DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY``
           archive_name = 'archive_name'
           full_archive_path = os.path.join('path', 'to', 'archive', 'archive_name')

           # Instance the backend.
           backend_instance = backend_class(
               archive_path=full_archive_path,
               archive_name=archive_name,
               readmode=False
            )

           # Get files to compress
           file1 = open('examplefile1.txt', 'r')
           file2 = open('examplefile2.txt', 'r')

           # Add file1 inside a folder named folder1
           # Add file2 inside a folder named folder2
           # The archive with content will now look like this
           # archive_name.zip
           #     - folder1
           #         - examplefile1.txt
           #     - folder2
           #         - examplefile2.txt
           backend_instance.add_file(os.path.join('folder1', 'examplefile1.txt'), file1)
           backend_instance.add_file(os.path.join('folder2', 'examplefile2.txt'), file2)

           # Close the backend
           backend_instance.close()

           # Read the archive as a fileobject
           # ``read_archive()`` returns a FileObject of the archive
           # This can for instance be passed to a HttpRequest.
           backend_instance.readmode = True
           fileobj = backend_instance.read_archive()


**************************************************
Datamodel API for caching metainfo about a archive
**************************************************
.. currentmodule:: devilry.devilry_compressionutil.models


.. automodule:: devilry.devilry_compressionutil.models
    :members:


Backend base classes
====================
.. currentmodule:: devilry.devilry_compressionutil.views

.. automodule:: devilry.devilry_compressionutil.views.backends_base
    :members:

