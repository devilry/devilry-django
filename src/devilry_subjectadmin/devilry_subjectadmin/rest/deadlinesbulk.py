from datetime import datetime
from django import forms
from django.db import transaction
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from djangorestframework.views import View
from djangorestframework.resources import FormResource, ModelResource
from djangorestframework.permissions import IsAuthenticated
from .auth import IsAssignmentAdmin
import hashlib

from devilry.apps.core.models import Deadline
from devilry.apps.core.models import AssignmentGroup
from devilry.utils.restformat import format_datetime
from devilry.utils.restformat import format_timedelta
from .group import GroupSerializer
from .errors import NotFoundError
from .errors import ValidationErrorResponse
#from .log import logger


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


def texthashmatch(texthash, text):
    if text == None:
        return bool(texthash) == False
    else:
        return texthash == sha1hash(text)


class DeadlinesBulkRest(View):
    """
    Handle deadlines on an assignment in bulk.

    # GET
    List all deadlines on an assignment with newest deadline firsts. Deadlines
    with exactly the same ``deadline`` and ``text`` are collapsed into a single
    entry in the list, with the number of groups listed.

    # POST
    Create a new deadline.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)

    def _serialize_deadline(self, deadline):
        """
        Serialize ``Deadline``-object as plain python.
        """
        bulkdeadline_id = encode_bulkdeadline_id(deadline)
        return {'bulkdeadline_id': bulkdeadline_id,
                'deadline': format_datetime(deadline.deadline),
                'in_the_future': deadline.deadline > self.now,
                'offset_from_now': format_timedelta(self.now - deadline.deadline),
                'url': reverse('devilry_subjectadmin_rest_deadlinesbulkinstance',
                               kwargs={'id': self.assignment_id,
                                       'bulkdeadline_id': bulkdeadline_id}),
                'text': deadline.text}

    def _get_distinct_deadlines(self, deadlines):
        distinct_deadlines = {}
        idformat = '{deadline}:{text_firstchar}'
        for deadline in deadlines:
            bulkid = encode_bulkdeadline_id(deadline)
            if bulkid in distinct_deadlines:
                distinct_deadlines[bulkid]['groupcount'] += 1
            else:
                serialized_deadline = self._serialize_deadline(deadline)
                serialized_deadline['groupcount'] = 1
                distinct_deadlines[bulkid] = serialized_deadline
        return distinct_deadlines.values()

    def _deadline_cmp(self, a, b):
        comp = cmp(b['deadline'], a['deadline']) # Order with newest first
        if comp == 0:
            # Order by text if deadline is equal. text==None will be last in the list
            return cmp(a['text'], b['text'])
        else:
            return comp

    def _aggregate_deadlines(self):
        deadlines = Deadline.objects.filter(assignment_group__parentnode=self.assignment_id)
        distinct_deadlines = self._get_distinct_deadlines(deadlines)
        distinct_deadlines.sort(self._deadline_cmp)
        return distinct_deadlines

    def get(self, request, id):
        self.assignment_id = id
        self.now = datetime.now()
        distinct_deadlines = self._aggregate_deadlines()
        return distinct_deadlines




class UpdateDeadlinesBulkRestForm(forms.Form):
    deadline = forms.DateTimeField(required=True)
    text = forms.CharField(required=False)


class UpdateDeadlinesBulkRestResource(FormResource):
    form = UpdateDeadlinesBulkRestForm

    def deadline(self, dct):
        return format_datetime(dct['deadline'])


class GroupsListResource(ModelResource):
    model = AssignmentGroup
    fields = ('id', 'name', 'etag', 'is_open', 'num_deliveries',
              'parentnode', 'feedback', 'candidates')

    def parentnode(self, instance):
        return int(instance.parentnode_id)

    def feedback(self, instance):
        return GroupSerializer(instance).serialize_feedback()

    def deadlines(self, instance):
        return GroupSerializer(instance).serialize_deadlines()

    #def tags(self, instance):
        #return GroupSerializer(instance).serialize_tags()

    #def examiners(self, instance):
        #return GroupSerializer(instance).serialize_examiners()

    def candidates(self, instance):
        return GroupSerializer(instance).serialize_candidates()



class UpdateDeadlinesBulkRest(View):
    """
    # About bulkdeadline_id
    The ``bulkdeadline_id`` is a generated string on this format:

        <datetime>--<texthash>

    - ``<datetime>`` is the datetime of the deadaline formatted as
      ``YYYY-MM-DDThh_mm_ss``.
    - ``<texthash>`` is the first character of
      the deadline text. If the deadline text is ``null`` or empty string,
      ``<texthash>`` will be an empty string.


    # PUT
    Update all deadlines matching the ``bulkdeadline_id`` given as the last
    item in the url path.

    # GET
    List groups in this deadline.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = UpdateDeadlinesBulkRestResource

    def _deadlineqry(self):
        assignment_id = self.kwargs['id']
        bulkdeadline_id = self.kwargs['bulkdeadline_id']
        deadline_datetime, texthash = decode_bulkdeadline_id(bulkdeadline_id)
        qry = Deadline.objects.filter(assignment_group__parentnode=assignment_id,
                                      deadline=deadline_datetime)
        qry = qry.select_related('assignment_group', 'assignment_group__feedback')
        qry = qry.prefetch_related('assignment_group__examiners',
                                   'assignment_group__examiners__user',
                                   'assignment_group__examiners__user__devilryuserprofile',
                                   'assignment_group__candidates',
                                   'assignment_group__candidates__student',
                                   'assignment_group__candidates__student__devilryuserprofile')
        # Filter out deadlines that do not match the texthash
        def hashmatch(deadline):
            match = texthashmatch(texthash, deadline.text)
            return match
        deadlines = filter(hashmatch, qry)
        if len(deadlines) == 0:
            raise NotFoundError('No deadline matching: {0}'.format(bulkdeadline_id))
        return deadlines

    def _as_groupobjects(self, deadlines):
        return map(lambda deadline: deadline.assignment_group, deadlines)

    def _create_response(self, deadline, groups):
        return {'bulkdeadline_id': encode_bulkdeadline_id(deadline),
                'deadline': deadline.deadline,
                'text': deadline.text,
                'groups': GroupsListResource().serialize(groups)}

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
            except ValidationError as e:
                raise ValidationErrorResponse(e)
            else:
                transaction.commit()
        return deadlines

    def get(self, request, id, bulkdeadline_id):
        deadlines = self._deadlineqry()
        groups = self._as_groupobjects(deadlines)
        return self._create_response(deadlines[0], groups)

    def put(self, request, id, bulkdeadline_id):
        bulkdeadline_id = self.kwargs['bulkdeadline_id']
        deadlines = self._deadlineqry()
        deadlines = self._update_deadlines(deadlines)
        groups = self._as_groupobjects(deadlines)
        return self._create_response(deadlines[0], groups)
