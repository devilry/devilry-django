from django.utils.translation import ugettext as _
from django.db import transaction
from django import forms
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.response import Response
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Period

from .auth import IsPeriodAdmin
from .errors import BadRequestFieldError


def _find_relatedexaminers_matching_tags(tags, relatedexaminers):
    examiners = []
    for relatedexaminer in relatedexaminers:
        for tag in tags:
            if relatedexaminer.tags and tag in relatedexaminer.tags:
                examiners.append(relatedexaminer.user)
                break
    return examiners


class CreateNewAssignmentDao(object):
    def _create_assignment(self, period, short_name, long_name, first_deadline,
                           publishing_time, delivery_types, anonymous):
        assignment = Assignment(parentnode=period, short_name=short_name,
                                long_name=long_name,
                                first_deadline=first_deadline,
                                publishing_time=publishing_time,
                                delivery_types=delivery_types,
                                anonymous=anonymous)
        assignment.full_clean()
        assignment.save()
        return assignment

    def _create_group_from_relatedstudent(self, assignment, relatedstudent,
                                          relatedexaminers):
        """
        Create an AssignmentGroup within the given ``assignment`` with tags and
        examiners from the given ``relatedstudent`` and ``relatedexaminers``.

        The examiners are set if an examiner share a tag with a student.

        Note that ``relatedexaminers`` is a parameter (as opposed to using
        assignment.parentnode...) because they should be queried for one time,
        not for each call to this method.
        """
        group = assignment.assignmentgroups.create()
        kw = dict(student=relatedstudent.user)
        if relatedstudent.candidate_id:
            kw['candidate_id'] = relatedstudent.candidate_id
        group.candidates.create(**kw)
        if relatedstudent.tags:
            tags = relatedstudent.tags.split(',')
            for tag in tags:
                group.tags.create(tag=tag)
            examiners = _find_relatedexaminers_matching_tags(tags, relatedexaminers)
            for examiner in examiners:
                group.examiners.create(user=examiner)
        return group

    def _create_deadline(self, group, deadline):
        return group.deadlines.create(deadline=deadline)

    def _add_all_relatedstudents(self, assignment, first_deadline,
                                 autosetup_examiners):
        if not first_deadline:
            raise BadRequestFieldError('first_deadline', _('Required when automatically adding related students'))
        if autosetup_examiners:
            relatedexaminers = assignment.parentnode.relatedexaminer_set.all()
        else:
            relatedexaminers = [] # If we have no related examiners, none will be added..
        for relatedstudent in assignment.parentnode.relatedstudent_set.all():
            group = self._create_group_from_relatedstudent(assignment,
                                                           relatedstudent,
                                                           relatedexaminers)
            self._create_deadline(group, first_deadline)

    def create(self, user, period,
               short_name, long_name, first_deadline, publishing_time,
               delivery_types, anonymous, add_all_relatedstudents,
               autosetup_examiners):
        assignment = self._create_assignment(period, short_name, long_name,
                                             first_deadline, publishing_time,
                                             delivery_types, anonymous)
        if add_all_relatedstudents:
            self._add_all_relatedstudents(assignment, first_deadline,
                                          autosetup_examiners)
        return assignment

    def lookup_period_create(self, user, period_id, *args, **kwargs):
        period = Period.objects.get(id=period_id)
        return self.create(user, period, *args, **kwargs)





class RestCreateNewAssignmentForm(forms.Form):
    short_name = forms.CharField(required=True)
    long_name = forms.CharField(required=True)
    first_deadline = forms.DateTimeField(required=False)
    publishing_time = forms.DateTimeField(required=True)
    delivery_types = forms.IntegerField(required=True)
    anonymous = forms.BooleanField(required=False)
    add_all_relatedstudents = forms.BooleanField(required=False)
    autosetup_examiners = forms.BooleanField(required=False)


class RestCreateNewAssignmentRoot(View):
    resource = FormResource
    form = RestCreateNewAssignmentForm
    permissions = (IsAuthenticated, IsPeriodAdmin)

    def __init__(self):
        self.dao = CreateNewAssignmentDao()

    def post(self, request, period_id):
        with transaction.commit_on_success():
            # Need to use a transaction since we potentially perform multiple changes.
            assignment = self.dao.lookup_period_create(self.user, period_id, **self.CONTENT)
            return Response(status=201, content=dict(id=assignment.id))
