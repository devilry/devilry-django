.. _simplified:


==========================================
Simplified API
==========================================

*The simplified API is under development.*

The simplified API is a simple task oriented API which simplifies the most
common needs. It is a API which lends itself naturally to be exposed
as a RESTful web service API. This API is the public interface for devilry in any
language and platform:

    - RESTful web services
    - javascript
    - serverside python
    - client libraries using the RESTful web API.

This means that a developer who has played around with the javascript in the
Devilry templates, can use the same API if he or she wants to develop a
serverside addon or a command-line script using the official devilry python
bindings.


What is it?
#####################################################################

The devilry core is very powerful and flexible. This unfortunatly makes it a
bit complex. The simplified API makes all the information provided by the core
available through a much more simple API. Instead of the recursive database
API provided by the core, developers get a API where they can say things like:

- give me all deliveries by this user on this assignent.
- update the feedback on this delivery
- get all files in this delivery
- ...


What is it not?
#####################################################################

You can access all data in the devilry core via the simplified API, but it is
limited to the most common ways of accessing this data. This means that you have
to use the core directly if you wish to make complex queries which is not needed
by a common *task*. To put it simple: It is not an API for doing things that are
not supported by the devilry web interface.




Example
#############

TODO: Create simplified API usage example.


Public API
#################

Every function and class in the public API is made available directly in
``devilry.simplified.NAME``.


.. automodule:: devilry.simplified
    :members: simplified_modelapi
    :no-members:

.. autoclass:: devilry.simplified.fieldspec.FieldSpec

.. autoclass:: devilry.simplified.exceptions.PermissionDenied

.. autoclass:: devilry.simplified.qryresultwrapper.QryResultWrapper
