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

    GET /path/to/api/
    Accept: application/json

However you can also use the ``_devilry_accept`` querystring parameter::

    GET /path/to/api/?_devilry_accept=application/json

Or suffix::

    GET /path/to/api/1.json

Note that suffix also works on ``/``, even if it looks a bit strange::

    GET /path/to/api/.json


Input content type
------------------

Normally you wont need to specify an input content type --- it will fall back
on the output content type. However, if you want to send data encoded in format,
and receive the response encoded in another, this is specified using
the ``Content-type`` HTTP header::

    GET /path/to/api/
    Accept: application/xml
    Content-type: application/json



API
############################

.. autoclass:: devilry.rest.restbase.RestBase
.. autoclass:: devilry.rest.restview.RestView
