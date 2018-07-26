==============
Update Devilry
==============

.. warning::

    These are general instructions that work if we only have code changes.
    Refer to the migration guide for each new version for the correct
    instructions.

.. note::

    Remember that you should run all these commands as the system user
    you created in :doc:`gettingstarted`. The exception is, of course,
    stopping/starting Supervisord if you use an init script.

1. Update the version of the ``devilry`` library in your ``~/devilrydeploy/requirements.txt``.

2. Stop Supervisord (or all your init script services etc. that run gunicorn or any ``venv/bin/manage.py`` commands).

3. Update Devilry using PIP::

    $ cd ~/devilrydeploy
    $ venv/bin/pip install -r requirements.txt

4. Apply database migrations (does nothing if there are no changes)::

    $ cd ~/devilrydeploy
    $ venv/bin/python manage.py migrate

5. Collect static files::

    $ cd ~/devilrydeploy
    $ venv/bin/python manage.py collectstatic

6. Start Supervisord (restart what you stopped in (2)).
