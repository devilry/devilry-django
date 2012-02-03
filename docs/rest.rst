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



API
############################

.. autoclass:: devilry.rest.restbase.RestBase
.. autoclass:: devilry.rest.restview.RestView
