from ..core import models
import utils


class GetQryResult(object):
    def __init__(self, fields, qry):
        self.fields = fields
        self.qry = qry

    def valuesQryset(self):
        return self.qry.values(*self.fields)


class Subjects(object):
    default_orderby = ['long_name']

    @classmethod
    def getqry(cls, user,
            limit=50, start=0, query="",
            orderby=default_orderby):
        fields = ['id', 'short_name', 'long_name']
        queryfields = ['short_name', 'long_name']
        qry = models.Subject.published_where_is_examiner(user)
        qry = utils.qry_common(qry, fields, query, queryfields, orderby,
                limit, start)
        return GetQryResult(fields, qry)


class Periods(object):
    default_orderby = ['long_name']

    @classmethod
    def getqry(cls, user,
            limit=50, start=0, query='', orderby=default_orderby,
            subject_short_name=None):
        fields = ['id', 'short_name', 'long_name', 'parentnode__short_name']
        queryfields = ['short_name', 'long_name', 'parentnode__short_name']
        qry = models.Period.published_where_is_examiner(user)
        if subject_short_name:
            qry = qry.filter(parentnode__short_name=subject_short_name)
        qry = utils.qry_common(qry, fields, query, queryfields, orderby,
                limit, start)
        return GetQryResult(fields, qry)


class Assignments(object):
    default_orderby = ["short_name"]

    @classmethod
    def getqry(cls, user,
            limit=50, start=0, query="", orderby=default_orderby,
            old=True, active=True, longnamefields=False,
            pointhandlingfields=False,
            subject_short_name=None, period_short_name=None):
        """
        List all old and active assignments. Provides the following
        information (fields) for each listed assignment by default:

            - id
            - short_name
            - long_name
            - parentnode__short_name *(Period short_name)*
            - parentnode__parentnode__short_name *(Subject short_name)*

        For documentation on the fields, see :class:`devilry.core.models.Assignment`.

        :param limit:
            Number of results.
        :param start:
            Offset where the result should start (If start is 10 and
            limit is 30, results 10 to 40 is returned, including both ends).
        :param old:
            Include assignments from old (not active) periods?
        :param active:
            Include assignments from old (not active) periods?
        :param orderby:
            Sort the result by this field. Must be one of:
            *id*, *short_name*, *long_name*, *publishing_time*, *pointscale*,
            *autoscale*, *maxpoints*, *attempts* or *must_pass*. See
            :class:`devilry.core.models.Assignment` for documentation on each of
            these fields.
        :param query:
            A query to limit the results.
        :param longnamefields:
            Include the *long_name* field of period and
            subject for each assignment in the result?
        :param pointhandlingfields:
            Include the *grade_plugin*, *pointscale*, *autoscale*,
            *maxpoints*, *attempts*, and *must_pass* fields for each assignment in
            the result? The *grade_plugin* field contains the (human readable and
            translated) label instead of the grade plugin key.

        :return: The requested assignments as a QuerySet.
        """
        fields = ['id', 'short_name', 'long_name',
                'parentnode__short_name',
                'parentnode__parentnode__short_name']
        if longnamefields:
            fields.append('parentnode__long_name')
            fields.append('parentnode__parentnode__long_name')
        queryfields = fields
        qry = models.Assignment.published_where_is_examiner(user, old=old,
                active=active)
        if subject_short_name and period_short_name:
            qry = qry.filter(parentnode__short_name=period_short_name,
                    parentnode__parentnode__short_name=subject_short_name)
        qry = utils.qry_common(qry, fields, query, queryfields, orderby,
                limit, start)
        return GetQryResult(fields, qry)


class Groups(object):
    default_orderby = ['id']

    @classmethod
    def getqry(cls, user,
            assignment_id, limit=50, start=0, orderby=default_orderby,
            deadlines=False, query=""):
        """
        List all groups in the given assignment. Provides the following
        information (fields) for each listed group by default:

            id
                A unique ID for the group.
            name
                Name of the group, or None if it has no name.
            canidates
                List of username or candidate number.
            examiners
                List of usernames.

        :param limit:
            Number of results.
        :param start:
            Offset where the result should start (If start is 10 and
            limit is 30, results 10 to 40 is returned, including both ends).
        :param orderby:
            Sort the result by this field. Must be one of:
            *id*, *is_open*, *status*, *points*, *scaled_points* or
            *active_deadline* (only if details is 1).
            See :class:`devilry.core.models.AssignmentGroup` for documentation on
            each of these fields.
        :param deadlines:
            Add deadlines? If True, the result will contain the following
            additional fields:

                deadlines
                    A list of deadlines for this group.
                active_deadline
                    The active deadline for this group.
        :param query:
            A query to limit the results.

        :return: The requested groups as a QuerySet.
        """
        queryfields = ['name', 'candidates__student__username']
        fields = ['id', 'name']
        qry = models.AssignmentGroup.published_where_is_examiner(user).filter(
                parentnode=assignment_id)
        qry = utils.qry_common(qry, fields, query, queryfields, orderby,
                limit, start)
        return GetQryResult(fields, qry)
