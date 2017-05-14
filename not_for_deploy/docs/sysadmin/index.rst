#####################
Devilry sysadmin docs
#####################

.. toctree::
   :maxdepth: 2

   gettingstarted
   authbackend
   celery
   supervisord
   webserver
   debug
   update
   autoset_empty_email_by_username
   managementcommands


Migration guides
================
If a minor version is not listed here, it is a code-only update, which means that
the :doc:`update guide <update>` is all you need.

.. toctree::
    :maxdepth: 1
    :glob:

    migrationguides/*
