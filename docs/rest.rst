.. _rest:

===============================================================
:mod:`devilry.rest` --- General purpose REST framework
===============================================================


.. currentmodule:: devilry.rest


About RESTful web services
##########################

http://en.wikipedia.org/wiki/Representational_State_Transfer#RESTful_web_services

Relation to restful
###################

Unlike :ref:`restful`, this is a general purpose REST interface library for
writing any RESTful interface, not just interfaces with a direct mapping to the
Django ORM.


.. _rest-for-users:

Using the REST APIs
#####################

If you are only using the rest APIs, and not creating them, this section is for you.


Content types
=============

The REST APIs generate data that can be serialized/deserialized on several formats:

- JSON --- application/json
- YAML --- application/yaml
- XML --- application/xml
- ExtJS flavoured JSON --- application/extjsjson


Output content type --- ACCEPT
------------------------------
The content type for output from the APIs is normally specified using a HTTP
accept header in the HTTP request::

    GET http://devilry.example.com/path/to/api/
    Accept: application/json

However you can also use the ``_devilry_accept`` querystring parameter::

    GET http://devilry.example.com/path/to/api/?_devilry_accept=application/json

Or suffix::

    GET http://devilry.example.com/path/to/api/1.json

Note that suffix also works on ``/``, even if it looks a bit strange::

    GET http://devilry.example.com/path/to/api/.json


Input content type
------------------

Normally you wont need to specify an input content type --- it will fall back
on the output content type. However, if you want to send data encoded in format,
and receive the response encoded in another, this is specified using
the ``Content-type`` HTTP header::

    GET http://devilry.example.com/path/to/api/
    Accept: application/xml
    Content-type: application/json


Parameters
==========

Parameters are given in the querystring (the stuff after ? in the url). For
example, if the ``/path/to/api/`` API required a numeric parameter named
``stuff``, we would specify it using::

    GET http://devilry.example.com/path/to/api/?stuff=10

Lets say the API also supported a ``search`` parameter, we could specify both
``stuff`` and ``search``::

    GET http://devilry.example.com/path/to/api/?stuff=10&search=something

Furthermore, other requests such as POST and PUT also uses the querystring for
parameters. So to create a new item in our fictional API, we would do something
like this::

    POST http://devilry.example.com/path/to/api/?stuff=10

    Some data here.



API
############################

RestBase
========
.. autoclass:: devilry.rest.restbase.RestBase

RestView
========
.. autoclass:: devilry.rest.restview.RestView

@indata
========
.. currentmodule:: devilry.rest.indata
.. automodule:: devilry.rest.indata
