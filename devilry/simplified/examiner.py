from django import forms

from devilry.core.models import Assignment, AssignmentGroup
import utils
import fields
from restview import RestView


class Assignments(RestView):

    class GetForm(forms.Form):
        format = forms.CharField(required=True)
        count = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=["short_name"])
        old = fields.BooleanWithFallbackField(fallbackvalue=True)
        active = fields.BooleanWithFallbackField(fallbackvalue=True)
        search = forms.CharField(required=False)
        longnamefields = fields.BooleanWithFallbackField()
        pointhandlingfields = fields.BooleanWithFallbackField()

    @classmethod
    def getqry(cls, user,
            count=50, start=0, orderby=["short_name"],
            old=True, active=True, search="", longnamefields=False,
            pointhandlingfields=False):
        """
        List all old and active assignments. Provides the following
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
            *id*, *short_name*, *long_name*, *publishing_time*, *pointscale*,
            *autoscale*, *maxpoints*, *attempts* or *must_pass*. See
            :class:`devilry.core.models.Assignment` for documentation on each of
            these fields.
        :param search:
            A query to limit the results.
        :param longnamefields:
            Include the *long_name* field of assignment, period and
            subject for each assignment in the result?
        :param pointhandlingfields:
            Include the *grade_plugin*, *pointscale*, *autoscale*,
            *maxpoints*, *attempts*, and *must_pass* fields for each assignment in
            the result? The *grade_plugin* field contains the (human readable and
            translated) label instead of the grade plugin key.

        :return: The requested assignments as a QuerySet.
        """
        orderfields = ["short_name",
                "parentnode__short_name",
                "parentnode__parentnode__short_name"]
        if longnamefields:
            orderfields.append("long_name")
            orderfields.append("parentnode__long_name")
            orderfields.append("parentnode__parentnode__long_name")
        searchfields = ["id"] + orderfields
        qry = Assignment.published_where_is_examiner(user, old=old,
                active=active)
        qry = utils.search_queryset(qry, search, searchfields)
        qry = utils.order_queryset(qry, orderby, orderfields)
        qry = qry.distinct()
        return utils.limit_queryset(qry, count, start)


class Groups(RestView):

    class GetForm(forms.Form):
        format = forms.CharField(required=True)
        count = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=["short_name"])
        deadlines = fields.BooleanWithFallbackField(fallbackvalue=False)
        search = forms.CharField(required=False)

    @classmethod
    def getqry(cls, user,
            assignment_id, count=50, start=0, orderby=["id"],
            deadlines=False, search=""):
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

        :param count:
            Number of results.
        :param start:
            Offset where the result should start (If start is 10 and
            count is 30, results 10 to 40 is returned, including both ends).
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
        :param search:
            A query to limit the results.

        :return: The requested groups as a QuerySet.
        """
        searchfields = ['name', 'candidates__student__username']
        orderfields = ['id', 'name']
        qry = AssignmentGroup.published_where_is_examiner(user).filter(
                parentnode=assignment_id)
        qry = utils.search_queryset(qry, search, searchfields)
        qry = utils.order_queryset(qry, orderby, orderfields)
        qry = qry.distinct()
        return utils.limit_queryset(qry, count, start)
