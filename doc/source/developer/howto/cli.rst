.. _developer-howto-cli:

================================================
Developing and extending the command line client
================================================



Command and general purpose subclasses
#######################################################################

.. currentmodule:: devilry.xmlrpc_client.cli

.. automodule:: devilry.xmlrpc_client.cli


Shortcuts for walking the entire assignment-tree 
#######################################################################

.. currentmodule:: devilry.xmlrpc_client.assignmenttree


The *assignment tree* is everything in the :ref:`node-tree <overview>` from
*Assignment* and down. The ``devilry.xmlrpc_client.assignmentsync`` module
provides a layer on top of the the examiner :ref:`XMLRPC
<developer-howto-xmlrpc>` making it easy to work with and sync a copy of the
assignment-tree on the filesystem.


Directory-tree format
=====================

The following directory-format is used::

    [path of assignment]
        .info
        [group members separated by '-']
            .info
            [time of delivery YYYY-MM-DD_hh.mm.ss]
                .info
                [feedback.server.[rst|txt]]
                files/
                    [files in the delivery]


Handling directory name duplicates
==================================

Assignment groups might have exactly the same members, and deliveries
might be delivered within the same second. We could just add *id* to
every AssignmentGroup and Delivery, but that would be ugly for something
so uncommon. So instead we just add id when needed. This leads to some
extra complexity (explained in next section).


Info-objects
============

Each directory in the assignment-tree has a hidden file named *.info* where
information about the item in the directory is stored.
:class:`AssignmentTreeWalker` use Info-objects to send the information in the
.info-file and the location of the .info-file to the functions which can be
overridden in subclasses.

Info-objects has two extra functions only used when duplicates is a
possibility:

    1. :meth:`Info.determine_location` determines and sets the correct
       directory-name in the info-object, but does not change anything
       on the filesystem. After calling this function
       :meth:`Info.get_dirpath` will return the correct directory.
    2. :meth:`Info.rename_if_required` is run to rename a already
       existing directory (adding id to the name) if determine_location
       returns False.

.. autoclass:: devilry.xmlrpc_client.assignmenttree.Info


AssignmentTreeWalker-objects
============================

AssignmentTreeWalker does not change anything on the filesystem or on the
server (see :class:`AssignmentSync` for that), but provides a base for any
operation needing to walk the assignment-tree using the *examiner xmlrpc*.

.. autoclass:: devilry.xmlrpc_client.assignmenttree.AssignmentTreeWalker


AssignmentSync
==============

Uses :class:`AssignmentTreeWalker` to sync all deliveries on any
active assignment where the current user is examiner to the filesystem.

.. autoclass:: devilry.xmlrpc_client.assignmenttree.AssignmentSync
