.. _developer-howto-cli:

================================================
Developing and extending the command line client
================================================



Command and general purpose subclasses
#######################################################################

.. currentmodule:: devilry.xmlrpc_client.command

.. automodule:: devilry.xmlrpc_client.command


Utilities
#######################################################################

.. currentmodule:: devilry.xmlrpc_client.utils


AssignmentTreeWalker
======================================================================

AssignmentTreeWalker does not change anything on the
filesystem or on the server, but provides a base for any operation
needing to walk the assignment-tree using the *examiner xmlrpc*.


Directory-tree format
---------------------

Even though this class does not create any directories, it does presume
a direcotry hierarchy::

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
----------------------------------

Assignment groups might have exactly the same members, and deliveries
might be delivered withing the same second. We could just add *id* to
every AssignmentGroup and Delivery, but that would be ugly for something
so uncommon. So instead we just add id when needed. This leads to some
extra complexity.

We use :class:`Info`-objects to distribute the directory-path to the
functions which can be overridden in subclasses. The info-objects has
two extra functions only used when duplicates is a possibility:

    1. :meth:`Info.determine_location` determines and sets the correct
       directory-name in the info-object, but does not change anything
       on the filesystem. After calling this function
       :meth:`Info.get_dirpath` will return the correct directory.
    2. :meth:`Info.rename_if_required` is run to rename a already
       existing directory (adding id to the name) if determine_location
       returns False.


API
---

.. autoclass:: devilry.xmlrpc_client.utils.AssignmentTreeWalker


AssignmentSync
======================================================================

.. autoclass:: devilry.xmlrpc_client.utils.AssignmentSync
