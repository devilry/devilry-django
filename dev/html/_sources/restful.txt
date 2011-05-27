.. _restful:


==========================================
RESTful web service API
==========================================

*Under development*

http://en.wikipedia.org/wiki/Representational_State_Transfer#RESTful_web_services

HTTP status codes
#####################################################################

200 OK
    The request was succesful. The requested data is returned.
400 Bad Request
    A parameter is invalid. The data contains an error message.
401 Unauthorized
    Authorization required.
403 Forbidden
    Not authorized to access this page.
404 Not found
    Resource not found at the given url.


/examiner/
#####################################################################

All urls in the /examiner/ path work on data where the authenticated user is
examiner.


assignments/
=====================================================================

.. function:: GET(count=50, start=0, orderby="short_name", old=0, active=1, search="", longnamefields=0, pointhandlingfields=0)

    List all old and active assignments. Should provide the following
    information (fields) for each listed assignment by default:

        - id
        - short_name
        - period__short_name (parentnode.short_name)
        - assignment__short_name (parentnode.parentnode.short_name)

    For documentation on the fields, see :class:`devilry.core.models.Assignment`.

    :param count:
        Number of results.
    :param start:
        Offset where the result should start (If start is 10 and
        count is 30, results 10 to 40 is returned, including both ends).
    :param old:
        Include assignments from old (not active) periods?
    :param active:
        Include assignments from old (not active) periods?
    :param orderby:
        Sort the result by this field. Must be one of:
        *id*, *short_name*, *long_name*, *id*, *publishing_time*, *pointscale*,
        *autoscale*, *maxpoints*, *attempts* or *must_pass*. See
        :class:`devilry.core.models.Assignment` for documentation on each of
        these fields.
    :param search: A query to limit the results.
    :param longnamefields: Include the *long_name* field of assignment, period and
        subject for each assignment in the result?
    :param pointhandlingfields:
        Include the *grade_plugin*, *pointscale*, *autoscale*,
        *maxpoints*, *attempts*, and *must_pass* fields for each assignment in
        the result? The *grade_plugin* field contains the (human readable and
        translated) label instead of the grade plugin key.

    :return: The requested assignments if all is OK.


groups/{assignment-id}/
=====================================================================

.. function:: GET(count=50, start=0, orderby="id", details=0, search="")

    List all groups in the given assignment.

    :param count: Number of results.
    :param start: Offset where the result should start (If start is 10 and
        count is 30, results 10 to 40 is returned, including both ends).
    :param orderby: Sort the result by this field. Must be one of:
        *id*, *is_open*, *status*, *points*, *scaled_points* or
        *active_deadline* (only if details is 1).
        See :class:`devilry.core.models.AssignmentGroup` for documentation on
        each of these fields.
    :param details: Add details? If 1, the result will contain the following
        additional fields:
    
        deadlines
            A list of deadlines for this group.
        active_deadline
            The active deadline for this group.
    :param search: A query to limit the results.

    :return: The requested groups if all is OK.


group/{group-id}
=====================================================================

.. function:: GET()

    Get all available information about the given group (not about any deliveries).


deliveries/{group-id}/
=========================================================================

.. function:: GET()

    List all deliveries by this group.


delivery/{delivery-id}
==========================================================================

.. function:: GET()

    Get all information about the delivery with the given delivery-id,
    including feedback. This view might choose between embedding and linking/referencing
    *files/*.

.. function:: PUT()

    Create or update feedback on the delivery.

.. function:: DELETE()

    Clear the feedback on the delivery.


files/{delivery-id}/
================================================================================

.. function:: GET()

    List all files in a delivery.


download-file/{file-id}
===================================================================================================

.. function:: GET()

    Download the requested file.


list-filearchive/{file-id}
=================================================================================================

.. function:: GET()

    List the contents of the file, if it is a supported archive format.


download-filearchive-file/{file-id}/path
=================================================================================================

.. function:: GET()

    Download a single file from within a supported archive format.
