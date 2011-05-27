.. _xmlrpc:

============
XMLRPC howto
============

Devilry exports some common functionality over *XMLRPC*. XMLRPC is a language
independent standard, so if you need to do some of the more common operations
in devilry, but don't know Python, the XMLRPC should be able to help.

All XMLRPC functions exported by a running Devilry server can be found at
*/xmlrpc/*. So if your server is running at http://example.com, the xmlrpc will
be available at http://example.com/xmlrpc/ (just visit the address in a browser
for documentation).



Creating a XMLRPC for your Devilry plugin
#########################################

It is very easy to export parts of your addons as a *XMLRPC* with the help of
the ``devilry.xmlrpc`` module. *XMLRPC* can be used to communicate with the
devilry server from any programming language with support for XMLRPC with
cookies over SSL.

We will explain how to use XMLRPC by explaining how the
``devilry.addons.xmlrpc_examiner`` module works. The module exports the most
common functionality required by *examiners*.

A function
----------

First of all we need some functions. XMLRPC works over HTTP, so they basically
work just like a normal django view. Therefore we choose to put our views in
*views.py*. First we have to define our function:

.. literalinclude:: /../../devilry/addons/xmlrpc_examiner/views.py
    :pyobject: list_deliveries


Make it into a XMLRPC-function
------------------------------

Next we need to create a :class:`devilry.xmlrpc.XmlRpc` object where we can
register our function::

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


Check if it is working
----------------------

To find out if it is working, just start the django test server and visit
http://localhost:8000/xmlrpc. The xmlrpc, in this case ``"examiner"`` should be
in the menu, and clicking on it will take you to it's documentation.


Using the XMLRPC
################

To connect to this xmlrpc you will need a xmlrpc client with cookies (and SSL
for production use). A example of this can be found in *exampleclient.py* found
in the Devilry xmlrpc-client_.

.. _xmlrpc-client: http://github.com/devilry/devilry-django/tree/master/xmlrpc-client/




Other stuff
###########

For examples of how to:

- write unit-tests.
- document arguments and constraints

You should check out the sourcecode for `devilry.addons.xmlrpc_examiner`_.

.. _`devilry.addons.xmlrpc_examiner`:
    http://github.com/devilry/devilry-django/tree/master/devilry/addons/xmlrpc_examiner


API
###

.. autoclass:: devilry.xmlrpc.XmlRpc
