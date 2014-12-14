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
from devilry.devilry_subjectadmin.rest.mixins import SelfdocumentingMixin
from .log import logger


def _find_relatedexaminers_matching_tags(tags, relatedexaminers):
    examiners = []
    for relatedexaminer in relatedexaminers:
        examinertags = relatedexaminer.tags.split(',')
        for tag in tags:
            if relatedexaminer.tags and tag in examinertags:
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

    def _copy_students_from_assignment(self, assignment, first_deadline,
                                       copyfromassignment,
                                       copy_examiners=False,
                                       only_copy_passing_groups=False):
        for copysourcegroup in copyfromassignment.assignmentgroups.all():
            if only_copy_passing_groups:
                if not copysourcegroup.feedback or not copysourcegroup.feedback.is_passing_grade:
                    continue
            group = assignment.assignmentgroups.create(name=copysourcegroup.name)
            for candidate in copysourcegroup.candidates.all():
                group.candidates.create(student=candidate.student,
                                        candidate_id=candidate.candidate_id)
            for tag in copysourcegroup.tags.all():
                group.tags.create(tag=tag.tag)
            if copy_examiners:
                for examiner in copysourcegroup.examiners.all():
                    group.examiners.create(user=examiner.user)
            if assignment.delivery_types != NON_ELECTRONIC:
                self._create_deadline(group, first_deadline)

    def _setup_students(self, assignment, first_deadline, setupstudents_mode,
                        setupexaminers_mode, copyfromassignment_id=None,
                        user=None, only_copy_passing_groups=False):
        if setupstudents_mode == 'do_not_setup':
            return
        if not first_deadline and assignment.delivery_types != NON_ELECTRONIC:
            raise BadRequestFieldError('first_deadline',
                                       _('Required when adding students.'))
        if setupstudents_mode == 'allrelated':
            autosetup_examiners = setupexaminers_mode == 'bytags'
            self._add_all_relatedstudents(assignment, first_deadline,
                                          autosetup_examiners)
        elif setupstudents_mode == 'copyfromassignment':
            if not isinstance(copyfromassignment_id, int):
                raise BadRequestFieldError('copyfromassignment_id', 'Must be an int, got {0!r}'.format(copyfromassignment_id))
            try:
                copyfromassignment = Assignment.objects.get(id=copyfromassignment_id,
                                                            parentnode=assignment.parentnode)
            except Assignment.DoesNotExist:
                raise BadRequestFieldError('copyfromassignment_id', 'Assignment with id={0} does not exist in this period.'.format(copyfromassignment_id))
            else:
                copy_examiners = False
                if setupexaminers_mode == 'copyfromassignment':
                    copy_examiners = True

                self._copy_students_from_assignment(assignment, first_deadline,
                                                    copyfromassignment,
                                                    copy_examiners=copy_examiners,
                                                    only_copy_passing_groups=only_copy_passing_groups)

        else:
            raise BadRequestFieldError('setupexaminers_mode', 'Invalid value: {0}'.format(setupstudents_mode))

        if setupexaminers_mode == 'make_authenticated_user_examiner':
            for group in assignment.assignmentgroups.all():
                group.examiners.create(user=user)

    def create(self, user, period,
               short_name, long_name, first_deadline, publishing_time,
               delivery_types, anonymous, setupstudents_mode,
               setupexaminers_mode, copyfromassignment_id,
               only_copy_passing_groups):
        assignment = self._create_assignment(period, short_name, long_name,
                                             first_deadline, publishing_time,
                                             delivery_types, anonymous)
        if setupstudents_mode != 'do_not_setup':
            self._setup_students(assignment, first_deadline,
                                 setupstudents_mode=setupstudents_mode,
                                 setupexaminers_mode=setupexaminers_mode,
                                 copyfromassignment_id=copyfromassignment_id,
                                 user=user,
                                 only_copy_passing_groups=only_copy_passing_groups)
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
                                         help_text='The initial deadline (YYYY-MM-DD HH:MM). Required if ``setupstudents_mode!="do_not_setup"``.')
    publishing_time = forms.DateTimeField(required=True, input_formats=datetime_input_formats,
                                          help_text='YYYY-MM-DD HH:MM')
    delivery_types = forms.IntegerField(required=True,
                                        help_text=', '.join(['{0}: {1}'.format(*choice) for choice in as_choices_tuple()]))
    anonymous = forms.BooleanField(required=False)
    copyfromassignment_id = forms.IntegerField(required=False,
                                               help_text='Copy from this assignment if ``setupstudents_mode=="copyfromassignment"``.')
    setupstudents_mode = forms.ChoiceField(required=False,
                                           choices=(('do_not_setup', 'Do not setup'),
                                                    ('allrelated', 'Add all related students.'),
                                                    ('copyfromassignment', 'Copy from ``copyfromassignment_id``.')),
                                           help_text='Specifies how to setup examiners. Ignored if ``setupstudents_mode=="do_not_setup"``.')
    setupexaminers_mode = forms.ChoiceField(required=False,
                                            choices=(('do_not_setup', 'Do not setup'),
                                                     ('bytags', 'Setup examiners by tags. If ``setupstudents_mode!="allrelated"``, this option is the same as selecting ``do_not_setup``.'),
                                                     ('copyfromassignment', 'Copy from ``copyfromassignment_id``. If ``setupstudents_mode!="copyfromassignment"``, this option is the same as selecting ``do_not_setup``.'),
                                                     ('make_authenticated_user_examiner', 'Make the authenticated user examiner on all groups.')),
                                            help_text='Specifies how to setup examiners. Ignored if ``setupstudents_mode=="do_not_setup"``.')
    only_copy_passing_groups = forms.BooleanField(required=False)


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
