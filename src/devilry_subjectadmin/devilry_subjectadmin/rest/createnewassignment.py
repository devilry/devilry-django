from django.utils.translation import ugettext as _
from django.db import transaction
from django import forms
from django.core.exceptions import ValidationError
from djangorestframework.resources import FormResource
from djangorestframework.response import Response
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import View

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Period
from devilry.apps.core.models.deliverytypes import as_choices_tuple
from devilry.apps.core.models.deliverytypes import NON_ELECTRONIC

from .auth import periodadmin_required
from .errors import BadRequestFieldError
from .errors import ValidationErrorResponse
from. errors import PermissionDeniedError
from .mixins import SelfdocumentingMixin
from .log import logger


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
            if assignment.delivery_types != NON_ELECTRONIC:
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




datetime_input_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']

class RestCreateNewAssignmentForm(forms.Form):
    period_id = forms.IntegerField(required=True,
                                   help_text='The ID of the period where you want to create the assignment.')
    short_name = forms.CharField(required=True)
    long_name = forms.CharField(required=True)
    first_deadline = forms.DateTimeField(required=False, input_formats=datetime_input_formats,
                                         help_text='The initial deadline (YYYY-MM-DD HH:MM). Required if add_all_relatedstudents is true.')
    publishing_time = forms.DateTimeField(required=True, input_formats=datetime_input_formats,
                                          help_text='YYYY-MM-DD HH:MM')
    delivery_types = forms.IntegerField(required=True,
                                        help_text=', '.join(['{0}: {1}'.format(*choice) for choice in as_choices_tuple()]))
    anonymous = forms.BooleanField(required=False)
    add_all_relatedstudents = forms.BooleanField(required=False,
                                                 help_text='Add all related students to individual groups on the assignment.')
    autosetup_examiners = forms.BooleanField(required=False,
                                             help_text='Automatically setup examiners on this assignment by matching tags on examiners and students registered on the period. Ignored unless ``add_all_relatedstudents`` is true.')


class RestCreateNewAssignmentResource(FormResource):
    form = RestCreateNewAssignmentForm

    def validate_request(self, data, files=None):
        """
        Remove ``id`` from input data to enable us to have it in models.
        """
        if 'id' in data:
            del data['id']
        return super(RestCreateNewAssignmentResource, self).validate_request(data, files)


class RestCreateNewAssignment(SelfdocumentingMixin, View):
    """
    Simplifies creating and setting up new assignments.
    """
    resource = RestCreateNewAssignmentResource
    permissions = (IsAuthenticated,)

    def __init__(self):
        self.dao = CreateNewAssignmentDao()

    def _require_periodadmin(self, user):
        if not 'period_id' in self.CONTENT:
            raise PermissionDeniedError('period_id is a required parameter.')
        period_id = self.CONTENT['period_id']
        periodadmin_required(user, period_id)

    def postprocess_docs(self, docs):
        return docs.format(paramteterstable=self.htmlformat_parameters_from_form())

    def post(self, request):
        """
        Create an assignment, and add related students if requested.

        ## Parameters
        {paramteterstable}
        """
        self._require_periodadmin(request.user)
        if self.CONTENT['first_deadline'] and self.CONTENT['delivery_types'] == NON_ELECTRONIC:
            raise BadRequestFieldError('first_deadline',
                                       # NOTE: We do not translate this because it is something the UI should handle to avoid ever getting this error.
                                       'Must be ``null`` when creating NON_ELECTRONIC assignment.')
        with transaction.commit_on_success():
            # Need to use a transaction since we potentially perform multiple changes.
            try:
                assignment = self.dao.lookup_period_create(self.user, **self.CONTENT)
            except ValidationError, e:
                transaction.rollback()
                raise ValidationErrorResponse(e)
            else:
                logger.info('User=%s created Assignment with id=%s', self.user, assignment.id)
                return Response(status=201, content=dict(id=assignment.id,
                                                         period_id=assignment.parentnode_id,
                                                         short_name=assignment.short_name,
                                                         long_name=assignment.long_name,
                                                         first_deadline=assignment.first_deadline,
                                                         anonymous=assignment.anonymous))
