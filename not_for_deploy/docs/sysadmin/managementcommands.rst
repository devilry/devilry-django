.. _managmentcommands:

**************************
Devilry Managment Commands
**************************
This section describe the managment commands available in devilry.
To learn more about Django and their administrative support visit the `django managment commands`_
page in their docs. The set of commands may be altered or extended by packages used in Devilry.

Django managment commands follow a strict and well defined interface and is easy to extend and customize.
More info can be found on the `custom django-admin commands`_ page.
Devilry provides the following commands to ease the administration tasks for Devilry maintainers.
If you find the list incomplete and or want a broader support, you are welcome to post an issue on the Devilry
project `issue tracker`_ at any time.

.. _issue tracker: https://github.com/devilry/devilry-django/issues?state=open

.. _django managment commands: https://docs.djangoproject.com/en/1.4/ref/django-admin/

.. _custom django-admin commands: https://docs.djangoproject.com/en/1.4/howto/custom-management-commands/

The source code of the commands can be found in the official Devilry repository in the
`superadmin managment commands`_ directory.

.. _superadmin managment commands: https://github.com/devilry/devilry-django/tree/master/src/devilry/devilry/apps/superadmin/management/commands

===============
devilry_nodeadd
===============
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_nodeadd <node path> <short name>

Creates a new node in the Devilry node hierarchy. To create a root node
use *None* as <node path>.

--admins
    Comma separated list of usernames to set as admins on the node

--long_name
    A longer and more descriptive name of the node.


==================
devilry_subjectadd
==================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_subjectadd <short name> --long-name <long name>

Creates a new subject within the devilry hierarchy. Short name and long name are required.

--long-name
    A longer and more descriptive name of the node.

--permission-groups
    The name of one or more permission groups of type `departmentadmin` or `subjectadmin`.


Full example + adding the subject to multiple permission groups ::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_subjectadd duck1010 --long-name "Duck1010" --permission-groups "Duck1010 admins" "Department admins"


===================================
devilry_permissiongroup_add_subject
===================================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_permissiongroup_add_subject <Subject short name> <Permission group name>

Adds a subject to a permission group. Subject short name and permission group name are required.


=======================
devilry_subjectadminadd
=======================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_subjectadminadd <subject-short_name> <admin username>

Add a user as admin on the specified subject.

=========================
devilry_subjectadminclear
=========================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_subjectadminclear <subject short name>

Removes all administrators from the specified subject.

=====================
devilry_subjectsearch
=====================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_subjectsearch <short name>

Search for a subject by short name. Matches any part of the name.

--short_name-only
    Only print short name (one line per short name)

=================
devilry_periodadd
=================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_periodadd <subject short name> <period short name>

Create a new period on a new subject.

--admins
    Comma separated list of usernames to set as admins on the node.

--long_name
    A longer and more descriptive name of the node.

--start-time
    The start time of the period on ISO format *"%Y-%m-%dT%H:%M"*.

--end-time
    The end time of the period on ISO format *"%Y-%m-%dT%H:%M"*.

--date-format
    The date format expressed in a format according to `strftime`_

    .. _strftime: http://docs.python.org/library/datetime.html#strftime-strptime-behavior'

======================
devilry_periodadminadd
======================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_periodadminadd <subject-short_name> <period-short-name> <admin-username>

Add a user as admin on the period.

========================
devilry_periodadminclear
========================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_periodadminclear <subject short name> <period short name>

Clear administrators on the the subject.

====================
devilry_periodsearch
====================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_periodsearch <period short name>

Searches for periods based on the specified short name

--short_name-only
    Only print short name (one line per short name)

=================================
devilry_periodsetrelatedexaminers
=================================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_periodsetrelatedexaminers <subject short name> <period short name>

Set related examiners on a period. Users are read from stdin, as a JSON encoded array of arguments to the RelatedExaminer model.
See `relatedexaminers.json`_ for an example.

.. _relatedexaminers.json: https://github.com/devilry/devilry-django/blob/master/devilry/devilry_superadmin/examples/relatedexaminers.json

--clearall
    Clear all related examiners before adding

================================
devilry_periodsetrelatedstudents
================================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_periodsetrelatedstudents <subject short name> <period short name>

Set related students on a period. Users are read from stdin, as a JSON encoded array of arguments to the RelatedStudent model.
See `relatedstudents.json`_ for an example.

.. _relatedstudents.json: https://github.com/devilry/devilry-django/blob/master/devilry/devilry_superadmin/examples/relatedstudents.json

--clearall
    Clear all related students before adding

========================
devilry_resave_all_users
========================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilrly_resave_all_users

Resaves all users. This command is useful if you have any apps that listens for `post_save` signals on User.

=======================
devilry_sync_candidates
=======================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_sync_candidates

Sync the cached fields in Candidate with the actual data from User.

===============
devilry_useradd
===============
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_useradd <username>

Creates a new user.

--email
    The user email address

--full_name
    Full name of the user

--superuser
    Make the user a superuser. Be careful this will give the user complete access to everything in Devilry.

--password
    Password for the user login credential.

Returns a non-zero value when the user already exists in Devilry.

===================
devilry_useraddbulk
===================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_useraddbulk

Reading usernames from `stdin`

--emailsuffix
    Email suffix are set on all users in the list. Example: <username>@example.com

===============
devilry_usermod
===============
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_usermod <username>

Modify the credentials of an existing user

--email
    The user email address

--full_name
    Full name of the user

--superuser
    Make the user a superuser. Be careful this will give the user complete access to everything in Devilry.

--normaluser
    Make the user a normal user, with access to everything within their rank in Devilry hierarchy

==================
devilry_usersearch
==================
::

    $ cd ~/devilrydeploy/
    $ venv/bin/manage.py devilry_usersearch <username>

Search for a user by username. Matches any part of the username.

--username-only
    Only print usernames

--no-email
    Only matching users without an email address.

--superusers
    Only matching superusers

--normalusers
    Only matching normalusers, everybody except superusers


.. _devilry_delete_periods:

======================
devilry_delete_periods
======================

You have the option to delete all semesters that ended before a given amount of months ago.
This will delete everything associated with a semester: assignments, permissions, groups,
deliveries(comments and files) ...

You will be given a preview of which semesters that will be deleted, and which subjects they belong to.
Initially empty subjects will not be deleted, but if all semesters for a subject are deleted, the subject
will be deleted as well. You have to confirm to begin the deletion.

This example will delete all semesters that ended before two months ago from now::

    $ cd ~/devilrydeploy/
    $ python manage.py devilry_delete_periods 2


.. _devilry_delete_users:

=============================
devilry_delete_inactive_users
=============================

You can delete inactive users, which means users that have not logged in after a specified datetime.
The script has a required argument `--inactive-since-datetime` and expects it to be a ISO formatted datetime string.

When running the script you will be prompted with a preview of all users that are to delete and can be skipped. After
that you will have to confirm that you want to delete the users.

This example will delete all users that has not logged in since the 3pm first of July 2016::

    $ cd ~/devilrydeploy/
    $ python manage.py devilry_delete_inactive_users --inactive-since-datetime "2016-07-01 15:00"

The script will delete:
 - All users not logged in since the provided datetime, and their personal info(phone, email).
 - Their permissions.

The script will NOT delete:
 - Deliveries, comments or files made by the deleted users, see :ref:`devilry_delete_periods` for deleting that data.


.. _devilry_anonymize_database:

==========================
devilry_anonymize_database
==========================

.. warning::

    DO NOT RUN THIS MANAGEMENT COMMAND ON THE PRODUCTION/LIVE SERVER.

    Copy the production/live database to a testserver and run the command for anonymizing the database there.


Often times, having a copy of a production/live database can be pretty useful when trying to debug certain issues,
rather than trying to reproduce issues locally. This is where anonymization of the database comes in handy.

This management command will anonymize all user related data, such as users last names, first names, usernames and
emails. All login information provided by Dataporten will be deleted, and all passwords are set to test.

Anonymizing user data
=====================

There are two modes for running the management command, default(no argument) and `fast` and all user data will be
anonymized but in different ways:

default-mode:
    **Username**: Random set of characters matching the length of the original username.

    **User lastname**: Random set of characters matching the length of the original lastname.

    **User fullname**: Random set of characters matching the length of the original fullname.

    **Email**: The prefix will be a random set of characters matching the original prefix length and the suffix is set to `@example.com`.

fast-mode:
    **Username**: Changes to the ID of the user object.

    **User lastname**: Changed to `Lastname`.

    **User fullname**: Changed to `Full Name`.

    **Email**: Changed to `<user_id>_<email_object_id>@example.com`.


Anonymizing comments and comment files
======================================
All comments will be anonymized, meaning the content of a comment is replaced with a lorem ipsum text.
The anonymization script does not save files at all, but files are associated with a CommentFile where the filename
information is anonymized.

Additional actions performed by the anonymization command
=========================================================
- All login information from dataporten is deleted.
- All passwords are set to 'test'.



Running the command with default mode
=====================================
To run the command with default mode::

    $ cd ~/devilrydeploy/
    $ python manage.py devilry_anonymize_database


Running the command with fast mode
==================================
To run the command with fast mode::

    $ cd ~/devilrydeploy/
    $ python manage.py devilry_anonymize_database --fast

