####################################
Compressed archives for filedownload
####################################

When files are added to a feedback they can be downloaded in bulk. A background task will then compress
the files, and the archive will be ready for download once the task is finished. The files can be downloaded as an
archive for each feedbackfeed. Examiners can download all files as a compressed archive on the assignment as well.

The files are compressed once a user tries to download them, and that specific archive will then be available to
everyone that has access to the feed or the assignment(for examiners). The archive will not be compressed again when
user tries to download it until a change has occured (new files are added or deleted).


Setup environment variable
==========================
Add the following to ``~/devilrydeploy/devilry_settings.py``::

    #: The directory where compressed archives are stored. Archives are compressed when examiners or students
    #: downloads files from an assignment or a feedbackset.
    DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY = '/path/to/directory/for/compressedarchives/'


Deleting compressed archives
============================

Compressed archives has a database table that defines some meta about the actual compressed archive on disk, such
as the path to the file, size etc. A compressed archive file should not be directly deleted, so a management command
is provided for this. This can be set up with for example a cron job for cleaning up compressed archives, or just run
manually.

This will remove entries in database table, as well as the actual files on disk.

**********************************************
Deleting compressed archives older than X days
**********************************************

Delete all compressed archives older than a given number of days::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py devilry_delete_compressed_archives --days 14


******************************
Delete all compressed archives
******************************

Delete all compressed archives::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py devilry_delete_compressed_archives --all


.. note::

    What if I deleted the compressed archive files on the disk?

    The compressed archives contains copies of the uploaded files, so you can just use::

        $ venv/bin/python manage.py devilry_delete_compressed_archives --all

    to make sure the database is cleaned up correctly. The ``devilry_delete_compressed_archives``
    handles files missing on disk, and just removes the corresponding database objects if the files
    are missing.

    A compressed archive will be generated again when a user tries to download the files in bulk.


***************
Recommendations
***************

- We generally recommend keeping the files at least for a couple of weeks, to avoid
  that examiners and admins need to recreate the ZIP file while the files are still
  relevant. This means that a cron-task running::

      $ venv/bin/python manage.py devilry_delete_compressed_archives --days 14

  on a daily basis should be a good starting point. The exact number of days will
  depend on how your courses use devilry, how much storage space you want use,
  and how much your users complain about having to wait to re-build the zip files.
- The disk size and performance requirements will depend a lot on the type of
  courses/assignments your devilry install has. We recommend monitoring the disk
  where the ``DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY`` directory resides, to
  be able to react by deleting files (using ``devilry_delete_compressed_archives``)
  or increasing the disk size when needed.
