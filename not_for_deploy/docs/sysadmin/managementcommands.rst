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
**django.py devilry_nodeadd <node path> <short name>**

Creates a new node in the Devilry node hierarchy. To create a root node
use *None* as <node path>.

--admins
    Comma separated list of usernames to set as admins on the node

--long_name
    A longer and more descriptive name of the node.


==================
devilry_subjectadd
==================
**django.py devilry_subjectadd <node path> <short name>**

Creates a new subject within the devilry hierarchy. The path and short name are required.

--admins
    Comma separated list of usernames to set as admins on the node

--long_name
    A longer and more descriptive name of the node.

=======================
devilry_subjectadminadd
=======================
**django.py devilry_subjectadminadd <subject-short_name> <admin username>** 

Add a user as admin on the specified subject.

=========================
devilry_subjectadminclear
=========================
**django.py devilry_subjectadminclear <subject short name>** 

Removes all administrators from the specified subject.

=====================
devilry_subjectsearch
=====================
**django.py devilry_subjectsearch <short name>** 

Search for a subject by short name. Matches any part of the name.

--short_name-only
    Only print short name (one line per short name)

=================
devilry_periodadd
=================
**django.py devilry_periodadd <subject short name> <period short name>**

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
**django.py devilry_periodadminadd <subject-short_name> <period-short-name> <admin-username>**

Add a user as admin on the period.

========================
devilry_periodadminclear
========================
**django.py devilry_periodadminclear <subject short name> <period short name>**

Clear administrators on the the subject.

====================
devilry_periodsearch
====================
**django.py devilry_periodsearch <period short name>**

Searches for periods based on the specified short name

--short_name-only
    Only print short name (one line per short name)

=================================
devilry_periodsetrelatedexaminers
=================================
**django.py devilry_periodsetrelatedexaminers <subject short name> <period short name>**

Set related examiners on a period. Users are read from stdin, as a JSON encoded array of arguments to the RelatedExaminer model. 
See `relatedexaminers.json`_ for an example. 

.. _relatedexaminers.json: https://github.com/devilry/devilry-django/blob/2.0.4/devilry/devilry_superadmin/examples/relatedexaminers.json

--clearall
    Clear all related examiners before adding

================================
devilry_periodsetrelatedstudents
================================
**django.py devilry_periodsetrelatedstudents <subject short name> <period short name>**

Set related students on a period. Users are read from stdin, as a JSON encoded array of arguments to the RelatedStudent model. 
See `relatedstudents.json`_ for an example.

.. _relatedstudents.json: https://github.com/devilry/devilry-django/blob/2.0.4/devilry/devilry_superadmin/examples/relatedstudents.json

--clearall
    Clear all related students before adding

========================
devilry_resave_all_users
========================
**django.py devilrly_resave_all_users**

Resaves all users. This command is useful if you have any apps that listens for `post_save` signals on **User**.

=======================
devilry_sync_candidates
=======================
**django.py devilry_sync_candidates**

Sync the cached fields in Candidate with the actual data from User.

===============
devilry_useradd
===============
**django.py devilry_userad <username>**

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
**django.py devilry_useraddbulk**

Reading usernames from `stdin`

--emailsuffix
    Email suffix are set on all users in the list. Example: <username>@example.com

===============
devilry_usermod
===============
**django.py devilry_usermod <username>**

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
**django.py devilry_usersearch <username>**

Search for a user by username. Matches any part of the username.

--username-only
    Only print usernames

--no-email
    Only matching users without an email address.

--superusers
    Only matching superusers

--normalusers
    Only matching normalusers, everybody except superusers

