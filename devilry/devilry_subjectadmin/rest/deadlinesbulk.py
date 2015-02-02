from django.utils.translation import ugettext as _
from datetime import datetime
import hashlib
from django import forms
from django.db import transaction
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from devilry.devilry_rest.serializehelpers import format_datetime
from devilry.devilry_rest.serializehelpers import format_timedelta
from djangorestframework.views import View
from djangorestframework.resources import FormResource, ModelResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import Response

from devilry.apps.core.models import Deadline
from devilry.apps.core.models import AssignmentGroup
from .group import GroupSerializer
from .errors import NotFoundError
from .errors import ValidationErrorResponse
from .errors import BadRequestFieldError
from .errors import PermissionDeniedError
from .auth import IsAssignmentAdmin
from .log import logger
from .fields import ListOfTypedField


ID_DATETIME_FORMAT = '%Y-%m-%dT%H_%M_%S'


def sha1hash(text):
    m = hashlib.sha1()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def encode_bulkdeadline_id(deadline):
    formatted_datetime = deadline.deadline.strftime(ID_DATETIME_FORMAT)
    if deadline.text:
        texthash = sha1hash(deadline.text)
    else:
        texthash = ''
    return '{0}--{1}'.format(formatted_datetime, texthash)

def decode_bulkdeadline_id(bulkdeadline_id):
    formatted_datetime, texthash = bulkdeadline_id.split('--')
    deadline = datetime.strptime(formatted_datetime, ID_DATETIME_FORMAT)
    return deadline, texthash


def deadlines_as_groupobjects(deadlines):
    return map(lambda deadline: deadline.assignment_group, deadlines)



def texthashmatch(texthash, text):
    if text == None or text == '':
        return bool(texthash) == False
    else:
        return texthash == sha1hash(text)

class GroupsListResource(ModelResource):
    model = Deadline
    fields = ('id', 'name', 'is_open', 'status', 'num_deliveries',
              'parentnode', 'feedback', 'candidates')

    def id(self, deadline):
        return int(deadline.assignment_group.id)

    def name(self, deadline):
        return deadline.assignment_group.name

    def is_open(self, deadline):
        return deadline.assignment_group.is_open

    def status(self, deadline):
        return deadline.assignment_group.get_status()

    def parentnode(self, deadline):
        return int(deadline.assignment_group.parentnode_id)

    def feedback(self, deadline):
        return GroupSerializer(deadline.assignment_group).serialize_feedback()

    def deadlines(self, deadline):
        return GroupSerializer(deadline.assignment_group).serialize_deadlines()

    def candidates(self, deadline):
        return GroupSerializer(deadline.assignment_group).serialize_candidates()


def create_deadlinedict(assignment_id, deadlines, now=None, autoserialize_groups=True):
    now = now or datetime.now()
    deadline = deadlines[0]
    groups = []
    if autoserialize_groups:
        groups = GroupsListResource().serialize(deadlines)
    bulkdeadline_id = encode_bulkdeadline_id(deadline)
    return {'bulkdeadline_id': bulkdeadline_id,
            'deadline': format_datetime(deadline.deadline),
            'in_the_future': deadline.deadline > now,
            'offset_from_now': format_timedelta(now - deadline.deadline),
            'url': reverse('devilry_subjectadmin_rest_deadlinesbulkinstance',
                           kwargs={'id': assignment_id,
                                   'bulkdeadline_id': bulkdeadline_id}),
            'text': deadline.text,
            'groups': groups} # Only provided on instance, not in list


class CreateOrUpdateForm(forms.Form):
    deadline = forms.DateTimeField(required=True)
    text = forms.CharField(required=False, widget=forms.Textarea)
    createmode = forms.TypedChoiceField(required=False,
                                        coerce=str,
                                        choices=[('failed', 'Only add deadline for groups with failing grade'),
                                                 ('failed-or-no-feedback', 'Only add deadline for groups with failing grade or no feedback'),
                                                 ('no-deadlines', 'Only add deadline for groups with no deadlines.'),
                                                 ('specific-groups', 'Specify a list of group IDs using the group_ids argument.')],
                                        help_text='Only used for POST')
    group_ids = ListOfTypedField(required=False,
                                 coerce=int,
                                 help_text='List of group IDs (int).')


class CreateOrUpdateResource(FormResource):
    form = CreateOrUpdateForm

    def validate_request(self, data, files=None):
        if 'bulkdeadline_id' in data:
            del data['bulkdeadline_id']
        return super(CreateOrUpdateResource, self).validate_request(data, files)



class DeadlinesBulkListOrCreate(View):
    """
    Handle deadlines on an assignment in bulk.

    # About bulkdeadline_id
    The ``bulkdeadline_id`` is a generated string on this format:

        <datetime>--<texthash>

    - ``<datetime>`` is the datetime of the deadaline formatted as
      ``YYYY-MM-DDThh_mm_ss``.
    - ``<texthash>`` is the hexdigested SHA-1 encoded deadline text (40
      characters). If the deadline text is ``null`` or empty string,
      ``<texthash>`` will be an empty string.

    # GET
    List all deadlines on an assignment with newest deadline firsts. Deadlines
    with exactly the same ``deadline`` and ``text`` are collapsed into a single
    entry in the list, with the groups as an attribute of the entry.

    ## Response
    A list of objects with the following attributes:

    - ``bulkdeadline_id`` (string): See _About bulkdeadline_id_ above.
    - ``deadline`` (string "yyyy-mm-dd hh:mm:ss"): The datetime of the deadline.
    - ``in_the_future`` (bool): Is this deadline in the future?
    - ``offset_from_now`` (object): Delta from _now_ to the deadline.
    - ``text`` (string|null): Deadline text.
    - ``url`` (string): The url of the API for the instance.
    - ``groups``: List of groups in the deadline. Each group object has the
      following attributes:

        - ``id``
        - ``name``
        - ``is_open``
        - ``num_deliveries``: Number of deliveries by the group on the deadline.
        - ``parentnode``: The assignment ID.
        - ``feedback``
        - ``candidates``


    # POST
    Create new deadline for many groups in the given assignment.
    If a group is closed, is is opened when adding a deadline (to allow
    students to start making deliveries).

    If any of the groups are already on this deadline, we fail with a 400 error
    code.

    ## Parameters
    - ``deadline`` (string "YYYY-MM-DD hh:mm:ss"): The datetime of the deadline.
    - ``text`` (string|null): Deadline text.
    - ``createmode`` (string): One of:
        - ``failed``: Only add deadline on groups where active feedback is failed.
        - ``failed-or-no-feedback``: Only add deadline on groups where active feedback is failed or empty (no feedback).
        - ``no-deadlines``: Only add deadline on groups that have no deadlines.
        - ``specific-groups``: Add deadline to the groups specified in ``group_ids``.
    - ``group_ids`` (list of int|null): List of group-ids used when ``createmode=="specific-groups"``.

    ## Returns
    Same as GET in the instance REST API.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = CreateOrUpdateResource

    def _get_distinct_deadlines(self, deadlines):
        distinct_deadlines = {}
        idformat = '{deadline}:{text_firstchar}'
        for deadline in deadlines:
            bulkid = encode_bulkdeadline_id(deadline)
            if not bulkid in distinct_deadlines:
                serialized_deadline = create_deadlinedict(assignment_id=self.assignment_id,
                                                          deadlines=[deadline],
                                                          autoserialize_groups=False,
                                                          now=self.now)
                distinct_deadlines[bulkid] = serialized_deadline
            distinct_deadlines[bulkid]['groups'].append(GroupsListResource().serialize(deadline))
        return distinct_deadlines.values()

    def _deadline_cmp(self, a, b):
        comp = cmp(b['deadline'], a['deadline']) # Order with newest first
        if comp == 0:
            # Order by text if deadline is equal. text==None will be last in the list
            return cmp(a['text'], b['text'])
        else:
            return comp

    def _aggregate_deadlines(self):
        qry = Deadline.objects.filter(assignment_group__parentnode=self.assignment_id)
        qry = qry.select_related('assignment_group', 'assignment_group__feedback')
        qry = qry.annotate(num_deliveries=Count('deliveries'))
        qry = qry.prefetch_related('assignment_group__examiners',
                                   'assignment_group__examiners__user',
                                   'assignment_group__examiners__user__devilryuserprofile',
                                   'assignment_group__candidates',
                                   'assignment_group__candidates__student',
                                   'assignment_group__candidates__student__devilryuserprofile')
        distinct_deadlines = self._get_distinct_deadlines(qry)
        distinct_deadlines.sort(self._deadline_cmp)
        return distinct_deadlines

    def get(self, request, id):
        self.assignment_id = id
        self.now = datetime.now()
        distinct_deadlines = self._aggregate_deadlines()
        return distinct_deadlines


    #
    # POST
    #

    def _query_creategroups(self):
        assignment_id = self.kwargs['id']
        createmode = self.CONTENT['createmode']
        if not createmode:
            raise BadRequestFieldError('createmode', '``createmode`` is a required POST parameter.')
        qry = Q(parentnode=assignment_id)
        if createmode == 'failed-or-no-feedback':
            qry &= Q(Q(feedback__isnull=True) | Q(feedback__is_passing_grade=False))
        elif createmode == 'failed':
            qry &= Q(feedback__is_passing_grade=False)
        elif createmode == 'no-deadlines':
            qry &= Q(Q(num_deadlines=0) | Q(last_deadline=None))
        elif createmode == 'specific-groups':
            group_ids = self.CONTENT['group_ids']
            if not group_ids:
                raise BadRequestFieldError('group_ids',
                                           '``group_ids`` is required when ``createmode=="specific-groups"``.')
            qry &= Q(id__in=group_ids)
        else:
            raise ValueError('This is a bug - we have forgotten to handle one of the choices.')
        groups = AssignmentGroup.objects.annotate(num_deadlines=Count('deadlines'))
        groups = groups.filter(qry)
        return groups

    def _add_deadlines(self):
        new_deadline = self.CONTENT['deadline']
        text = self.CONTENT['text']
        deadlines = []
        with transaction.commit_manually():
            try:
                groups = self._query_creategroups()
                if len(groups) == 0:
                    raise BadRequestFieldError('createmode',
                                               _('The given option did not match any groups.'))
                for group in groups:
                    deadline = Deadline(assignment_group=group)
                    deadline.deadline = new_deadline
                    deadline.text = text
                    deadline.full_clean()
                    deadline.save()
                    deadlines.append(deadline)
                    logger.info('User=%s created Deadline id=%s (%s)', self.user, deadline.id, deadline.deadline)
            except ValidationError as e:
                transaction.rollback()
                raise ValidationErrorResponse(e)
            except Exception as e:
                transaction.rollback()
                raise
            else:
                transaction.commit()
        return deadlines

    def post(self, request, id):
        deadlines = self._add_deadlines()
        groups = deadlines_as_groupobjects(deadlines)
        assignment_id = self.kwargs['id']
        content = create_deadlinedict(assignment_id=assignment_id,
                                      deadlines=deadlines)
        return Response(status=201, content=content)



class DeadlinesBulkUpdateReadOrDelete(View):
    """
    # GET

    ## Returns
    An object with the following attributes:

    - ``bulkdeadline_id`` (string): See _About bulkdeadline_id_ in the [list api](./).
    - ``deadline`` (string "yyyy-mm-dd hh:mm:ss"): The datetime of the deadline.
    - ``in_the_future`` (bool): Is this deadline in the future?
    - ``offset_from_now`` (object): Delta from _now_ to the deadline.
    - ``text`` (string|null): Deadline text.
    - ``url`` (string): The url of this API.
    - ``groups``: List of groups in the deadline.

    # PUT
    Update all deadlines matching the ``bulkdeadline_id`` given as the last
    item in the url path.

    ## Parameters
    - ``deadline`` (string "YYYY-MM-DD hh:mm:ss"): The datetime of the deadline.
    - ``text`` (string|null): Deadline text.
    - ``group_ids`` (list of int|null): List of group-ids. If this is a non-empty
      list, only deadlines matching the ``bulkdeadline_id`` and have their group-id in
      this list are updated.

    ## Returns
    Same as GET.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = CreateOrUpdateResource

    def _deadlineqry(self, group_ids=None):
        assignment_id = self.kwargs['id']
        bulkdeadline_id = self.kwargs['bulkdeadline_id']
        deadline_datetime, texthash = decode_bulkdeadline_id(bulkdeadline_id)

        qry = Q(assignment_group__parentnode=assignment_id) & Q(deadline=deadline_datetime)
        if group_ids:
            qry &= Q(assignment_group_id__in=group_ids)

        queryset = Deadline.objects.filter(qry)
        queryset = queryset.annotate(num_deliveries=Count('deliveries'))
        queryset = queryset.select_related('assignment_group', 'assignment_group__feedback')
        queryset = queryset.prefetch_related('assignment_group__examiners',
                                   'assignment_group__examiners__user',
                                   'assignment_group__examiners__user__devilryuserprofile',
                                   'assignment_group__candidates',
                                   'assignment_group__candidates__student',
                                   'assignment_group__candidates__student__devilryuserprofile')
        # Filter out deadlines that do not match the texthash
        def hashmatch(deadline):
            match = texthashmatch(texthash, deadline.text)
            return match
        deadlines = filter(hashmatch, queryset)
        if len(deadlines) == 0:
            raise NotFoundError('No deadline matching: {0}'.format(bulkdeadline_id))
        return deadlines

    def _create_response(self, deadlines):
        assignment_id = self.kwargs['id']
        return create_deadlinedict(assignment_id=assignment_id,
                                   deadlines=deadlines)

    #
    # GET
    #
    def get(self, request, id, bulkdeadline_id):
        deadlines = self._deadlineqry()
        return self._create_response(deadlines)


    #
    # PUT
    #

    def _update_deadlines(self, deadlines):
        new_deadline = self.CONTENT['deadline']
        text = self.CONTENT['text']
        with transaction.commit_manually():
            try:
                for deadline in deadlines:
                    deadline.deadline = new_deadline
                    deadline.text = text
                    deadline.full_clean()
                    deadline.save()
                    logger.info('User=%s updated Deadline id=%s (%s)', self.user, deadline.id, deadline.deadline)
            except ValidationError as e:
                transaction.rollback()
                raise ValidationErrorResponse(e)
            else:
                transaction.commit()
        return deadlines

    def put(self, request, id, bulkdeadline_id):
        group_ids = self.CONTENT['group_ids']
        deadlines = self._deadlineqry(group_ids)
        deadlines = self._update_deadlines(deadlines)
        return self._create_response(deadlines)



    #
    #
    # DELETE
    #
    #
    def _delete_deadline(self, deadline):
        deadlineid = deadline.id
        deadlineident = unicode(deadline)
        if deadline.can_delete(self.user):
            deadline.delete()
            logger.info('User=%s deleted Deadline id=%s (%s)', self.user, deadlineid, deadlineident)
            return deadlineid
        else:
            logger.info(('User=%s tried to delete Deadline id=%s (%s). They where rejected '
                         'because of lacking permissions.'),
                        self.user, deadlineid, deadlineident)
            msg = ('Not permitted to delete Deadline with id={deadlineid}. '
                   'Only superusers can delete deadlines with deliveries.')
            raise PermissionDeniedError(msg.format(deadlineid=deadlineid))

    def delete(self, request, id, bulkdeadline_id):
        deadlines = self._deadlineqry()
        deadline_ids = []
        with transaction.commit_manually():
            try:
                for deadline in deadlines:
                    deadline_ids.append(self._delete_deadline(deadline))
            except PermissionDeniedError, e:
                transaction.rollback()
                raise
            else:
                transaction.commit()
        return {'success': True,
                'deleted_deadline_ids': deadline_ids}
