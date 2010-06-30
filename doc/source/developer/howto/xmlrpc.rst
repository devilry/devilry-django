.. _developer-howto-xmlrpc:

============
XMLRPC howto
============

It is very easy to export parts of your addons as a *XMLRPC* with the help of
the ``devilry.xmlrpc`` module. *XMLRPC* can be used to communicate with the
devilry server from any programming language with support for XMLRPC with
cookies over SSL.

We will explain how to use XMLRPC by explaining how the
``devilry.addons.xmlrpc_examiner`` module works. The module exports the most
common functionality required by *examiners*.


Getting started
###############

A function
----------

First of all we need some functions. XMLRPC works over HTTP, so they basically
work just like a normal django view. Therefore we choose to put our views in
*views.py*. First we have to define our function:

.. literalinclude:: /../../devilry/addons/xmlrpc_examiner/views.py
    :pyobject: list_deliveries


Make it into a XMLRPC-function
------------------------------

Next we need to create a :ref:`devilry.xmlrpc.XmlRpc
<ref-devilry.xmlrpc>` object where we can register our function::

    doc = """The functions required to do the most common operations required by
    a examiner."""

    rpc = XmlRpc('examiner', 'devilry-xmlrpc-examiner', doc)

Then we decorate our function with ``rpc.rpcdec_login_required``::

    @rpc.rpcdec_login_required()
    def list_deliveries(request, assignmentgroup_id):
        ...
Urls
----

At last we need to add the ``rpc`` object to ``urls.py``:

.. literalinclude:: /../../devilry/addons/xmlrpc_examiner/urls.py


Usage
-----

TODO


Functions with arguments and more
#################################

TODO
