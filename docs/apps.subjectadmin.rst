.. _apps.subjectadmin:

==============================================================
:mod:`devilry.apps.subjectadmin` --- Subject administrator GUI
==============================================================


About the app
####################

The *subjectadmin* app provides a GUI for administrator on Subject, Period and
Assignment, including a dashboard.



JavaScript API
##############

The application is mostly written in JavaScript, so check out the
*subjectadmin* package in the `Javascript API <javascript>`_.


Errors/exceptions
#################

.. automodule:: devilry.apps.subjectadmin.rest.errors

Authentification
################
.. automodule:: devilry.apps.subjectadmin.rest.auth

Group management
################

REST API
========


/ --- List
---------------------

Get list of all related students::

    GET <APPPREFIX>/rest/group/?assignmentid=1&_devilry_accept=application/json

    [{ // Group 1....
        "name": null,
        "tags": ['group1'],
        "students": [{
            "student__devilryuserprofile__full_name": "The Student1",
            "candidate_id": null,
            "student__username": "student1",
            "student__email": "student1@example.com"
        }],
        "feedback__is_passing_grade": true,
        "deadlines": [{
            "deadline": "2011-12-06T07:23:02"
        }],
        "examiners": [{
            "user__username": "examiner0",
            "user__email": "examiner0@example.com",
            "user__devilryuserprofile__full_name": null
        }],
        "feedback__points": 14,
        "feedback__grade": "g14",
        "is_open": false,
        "feedback__save_timestamp": "2012-02-04T07:23:07",
        "id": 2
    }, {
        // Group 2 ....
    }]


API
===

.. automodule:: devilry.apps.subjectadmin.rest.group


Related user management
##########################

REST API
========

/ --- List
---------------------

Get list of all related students::

    GET <APPPREFIX>/rest/relatedstudent/?periodid=1&_devilry_accept=application/json

    [{
        "user__username": "student0",
        "user_id": 11,
        "tags": "tag1,tag2",
        "user__devilryuserprofile__full_name": "The Student0",
        "candidate_id": "secretcand0",
        "user__email": "student0@example.com",
        "id": 1
    }, {
        // Second related student ...
    }]

The only difference required to get examiners is to change to
``relatedexaminer`` in the URL.
    

API
===
.. automodule:: devilry.apps.subjectadmin.rest.relateduser
