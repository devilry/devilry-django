.. _restful:


==========================================
RESTful web service API
==========================================


/examiner/
#######################################################

All urls in the /examiner/ path work on data where the authenticated user is
examiner.


Error status
=====================================================================

200 OK
    The request was succesful. The requested data is returned.
400 Bad Request
    A parameter is invalid. The data contains an error message.


/examiner/assignments/
=====================================================================

.. function:: get(count=50, start=0, orderby="short_name", old=0, active=1, qry="*")

    Get all old and active assignments.

    :param count: Number of results.
    :param start: Offset where the result should start (If start is 10 and
        count is 30, results 10 to 30 is returned).
    :param old: Show assignments from old (not active) periods?
    :param active: Show assignments from old (not active) periods?
    :param orderby: Sort the result by this field. Must be one of:
        *id*, *short_name*, *long_name*, *id*, *publishing_time*, *pointscale*,
        *autoscale*, *maxpoints*, *attempts* or *must_pass*. See
        :class:`devilry.core.models.Assignment` for documentation on each of
        these fields.
    :param qry: A query to limit the results.

    :return: The requested assignments if all is OK.

/examiner/assignments/{assignment-id}/
=====================================================================

.. function:: get(count=50, start=0, orderby="id", details=0, qry="*")

    List all groups in the given assignment.

    :param count: Number of results.
    :param start: Offset where the result should start (If start is 10 and
        count is 30, results 10 to 30 is returned).
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
    :param qry: A query to limit the results.

    :return: The requested groups if all is OK.


/examiner/assignments/{assignment-id}/{group-id}/
=====================================================================

.. function:: get()

    Get all available information about the given group (not about any deliveries).


/examiner/assignments/{assignment-id}/{group-id}/deliveries/
=========================================================================

.. function:: get()

    List all deliveries by this group.


/examiner/assignments/{assignment-id}/{group-id}/deliveries/{delivery-id}/
==========================================================================

.. function:: get()

    Get all information about the delivery with the given delivery-id,
    including feedback. This view might choose between embedding and linking/referencing
    *files/*.


/examiner/assignments/{assignment-id}/{group-id}/deliveries/{delivery-id}/files/
================================================================================

.. function:: get()

    List all files in a delivery.


/examiner/assignments/{assignment-id}/{group-id}/deliveries/{delivery-id}/files/{filename}
===================================================================================================

.. function:: get()

    Download the requested file.


/examiner/assignments/{assignment-id}/{group-id}/deliveries/{delivery-id}/files/{filename}/view
===============================================================================================

.. function:: get()

    View the requested file. This URL is not suited for all content-types, but
    in some, like HTML, this should give a preview of the file instead of
    offering a download.


/examiner/assignments/{assignment-id}/{group-id}/deliveries/{delivery-id}/files/{filename}/browse
=================================================================================================

.. function:: get()

    List the contents of the file, if it is a supported archive format.
