#####################
Devilry sysadmin docs
#####################

.. toctree::
   :maxdepth: 2

   automated_doc_build_test
   gettingstarted
   authbackend
   rq
   rq_email
   supervisord
   webserver
   sentry
   logging
   debug
   update
   autoset_empty_email_by_username
   managementcommands
   dataporten_setup
   branding
   devilry_settings
   compressed_archive_setup
   editable_ui_messages
   message_framework


Importing data from Devilry v2
==============================
Dump data from Devilry v2 and import to Devilry v3.

.. toctree::

    migrate_data_from_v2_to_v3


Migration guides
================
If a minor version is not listed here, it is a code-only update, which means that
the :doc:`update guide <update>` is all you need.

.. toctree::
    :maxdepth: 1
    :glob:

    migrationguides/*
