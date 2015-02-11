.. _update:

==============
Update Devilry
==============

.. warning::
    These are general instructions that work if we only have code changes.
    Refer to the migration guide for each new version for the correct
    instructions.

.. note::
    Remember that you should run all these commands as the system user
    you created in the :ref:`Build Devilry guide <deploy>`.
    The exception is, of course, stopping/starting Supervisord if you use an
    init script.

1. Update the ``REVISION`` in the ``extends``-attribute in the ``[buildout]`` section of your
   ``buildout.cfg`` as explained in :ref:`configure_buildout`.

2. Stop Supervisord. If you did not setup an init-script, you can use the PID-file
   in ``/path/to/devilrybuild/var/supervisord.pid`` unless you have configured
   it to be somewhere else. See: :ref:`supervisord-configure`.

3. Run buildout::

    $ bin/buildout "buildout:parts=download-devilryrepo" && bin/buildout
    $ bin/django.py collectstatic --noinput

4. Start Supervisord. If you have not created an init-script (see See:
   :ref:`supervisord-configure`), start Supervisord manually as explained in
   :ref:`run-supervisord-for-production`.
