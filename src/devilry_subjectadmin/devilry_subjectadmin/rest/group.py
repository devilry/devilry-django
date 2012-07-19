from django.db import transaction
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import Response
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView
from djangorestframework.views import InstanceModelView
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Delivery

from .errors import ValidationErrorResponse
from .errors import NotFoundError
from .auth import IsAssignmentAdmin
from .fields import ListOfDictField
from .fields import DictField
from .mixins import SelfdocumentingMixin


class IsAssignmentAdminAssignmentIdKwarg(IsAssignmentAdmin):
    ID_KWARG = 'assignment_id'



class GroupSerializer(object):
    """
    Serialize AssignmentGroup objects and related data.
    """
    def __init__(self, group):
        self.group = group

    def _serialize_deadline(self, deadline):
        return {'id': deadline.id,
                'deadline': deadline.deadline}

    def serialize_deadlines(self):
        return map(self._serialize_deadline, self.group.deadlines.all())

    def serialize_feedback(self):
        feedback = self.group.feedback
        if feedback:
            return {'id': feedback.id,
                    'grade': feedback.grade,
                    'points': feedback.points,
                    'is_passing_grade': feedback.is_passing_grade,
                    'save_timestamp': feedback.save_timestamp}
        else:
            return None

    def _serialize_user(self, user):
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.devilryuserprofile.full_name}

    def _serialize_examiner(self, examiner):
        return {'id': examiner.id,
                'user': self._serialize_user(examiner.user)}

    def serialize_examiners(self):
        return map(self._serialize_examiner, self.group.examiners.all())

    def _serialize_candidate(self, candidate):
        return {'id': candidate.id,
                'candidate_id': candidate.candidate_id,
                'user': self._serialize_user(candidate.student)}

    def serialize_candidates(self):
        return map(self._serialize_candidate, self.group.candidates.all())


class GroupManager(object):
    def __init__(self, assignment_id, group_id=None):
        self.assignment_id = assignment_id
        if group_id:
            self.group = AssignmentGroup.objects.get(parentnode_id=assignment_id,
                                                     id=group_id)
        else:
            self.group = AssignmentGroup(parentnode_id=assignment_id)
        self.serializer = GroupSerializer(self.group)

    def get_group_from_db(self):
        return AssignmentGroup.objects.get(id=self.group.id)

    def update_group(self, name, is_open):
        self.group.name = name
        self.group.is_open = is_open
        self.group.save()

    def _get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist, e:
            raise ValidationError('User with ID={0} does not exist'.format(user_id))

    def _create_examiner(self, user_id):
        user = self._get_user(user_id)
        try:
            self.group.examiners.create(user=user)
        except IntegrityError, e:
            raise ValidationError(_('The same user can not be examiner multiple times on the same group.'))

    def update_examiners(self, examinerdicts):
        """
        Update examiners from examinerdicts. Only cares about the following dict keys:

            id
                If this is ``None``, we create a new examiner.
            user (a dict)
                If ``id==None``, we use ``user['id']`` to find the user.

        Any examiner not identified by their ``id`` in ``examinerdicts`` is DELETED.
        """
        to_delete = {}
        for examiner in self.group.examiners.all():
            to_delete[examiner.id] = examiner
        for examinerdict in examinerdicts:
            examiner_id = examinerdict['id']
            isnew = examiner_id == None
            if isnew:
                user_id = examinerdict['user']['id']
                self._create_examiner(user_id)
            else:
                # Can not change existing examiners, only delete them
                del to_delete[examiner_id] # Remove existing from to_delete (thus, to_delete will be correct after the loop)
        for examiner in to_delete.itervalues():
            examiner.delete()

    def _create_candidate(self, user_id, candidate_id):
        user = self._get_user(user_id)
        self.group.candidates.create(student=user,
                                     candidate_id=candidate_id)

    def _update_candate(self, existing_candidate, candidate_id):
        has_changes = existing_candidate.candidate_id != candidate_id
        if has_changes:
            existing_candidate.candidate_id = candidate_id
            existing_candidate.save()

    def update_candidates(self, candidatedicts):
        """
        Update candidates from candidatedicts. Only cares about the following dict keys:

            id
                If this is ``None``, we create a new candidate.
            candidate_id
                Always updated, and always set when creating. May be ``None``.
            user (a dict)
                If ``id==None``, we use ``user['id']`` to find the user.

        Any existing candidate not identified by their ``id`` in
        ``candidatedicts`` is DELETED.
        """
        existing_by_id = {}
        for candidate in self.group.candidates.all():
            existing_by_id[candidate.id] = candidate
        for candidatedict in candidatedicts:
            candidate_id = candidatedict['id']
            isnew = candidate_id == None
            if isnew:
                user_id = candidatedict['user']['id']
                candidate_id = candidatedict['candidate_id']
                self._create_candidate(user_id=user_id, candidate_id=candidate_id)
            else:
                existing_candidate = existing_by_id[candidate_id]
                self._update_candate(existing_candidate, candidatedict['candidate_id'])
                del existing_by_id[candidate_id] # Remove existing from existing_by_id (which becomes to_delete) (thus, to_delete will be correct after the loop)
        to_delete = existing_by_id
        for candidate in to_delete.itervalues():
            candidate.delete() # TODO: Split candidates instead of DELETE




class UserField(DictField):
    class Form(forms.Form):
        id = forms.IntegerField(required=True)

        # These are ignored, however to work with the listing, we allow them in post/put data
        username = forms.CharField(required=False)
        email = forms.CharField(required=False)
        full_name = forms.CharField(required=False)

class TagsField(ListOfDictField):
    class Form(forms.Form):
        tag = forms.CharField()

class CandidatesField(ListOfDictField):
    class Form(forms.Form):
        id = forms.IntegerField(required=False)
        candidate_id = forms.CharField(required=False)
        user = UserField(required=False)

class DeadlinesField(ListOfDictField):
    class Form(forms.Form):
        deadline = forms.DateTimeField()

class ExaminersField(ListOfDictField):
    class Form(forms.Form):
        id = forms.IntegerField(required=False)
        user = UserField(required=False)

class GroupForm(forms.Form):
    name = forms.CharField(required=True)
    is_open = forms.BooleanField(required=False)
    #tags = TagsField(required=False)
    candidates = CandidatesField(required=False)
    #deadlines = DeadlinesField(required=False)
    examiners = ExaminersField(required=False)


class GroupResource(ModelResource):
    model = AssignmentGroup
    fields = ('id', 'name', 'etag', 'is_open', 'num_deliveries',
              'parentnode', 'feedback', 'deadlines', 'examiners', 'candidates')

    def serialize_model(self, instance):
        data = super(GroupResource, self).serialize_model(instance)
        if not 'num_deliveries' in data:
            # This is used when working directly with the instance. The listing
            # (query) annotates this field instead of querying for each object
            data['num_deliveries'] = Delivery.objects.filter(deadline__assignment_group=instance).count()
        return data

    def parentnode(self, instance):
        if isinstance(instance, self.model):
            return int(instance.parentnode_id)

    def feedback(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_feedback()

    def deadlines(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_deadlines()

    def examiners(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_examiners()

    def candidates(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_candidates()



feedback_docs = """The active feedback. NULL/None or a dict/object with the following attributes:

- ``grade`` (string): The grade.
- ``points`` (int): Number of points
- ``save_timestamp`` (iso datetime): When the feedback was created.
- ``is_passing_grade`` (boolean): Is this a passing grade?
- ``parentnode`` (int): The assignment ID.
"""

candidates_docs = """List of objects/maps with the following attributes:

- ``id``: ID of the candidate object in the database.
- ``candidate_id`` (string): The candidate ID used on anonymous assignments.
- ``user``: Object/map with the following attributes:
    - ``username``: (string)
    - ``email``: string
    - ``full_name``: string
"""
examiners_docs = """List of objects/maps with the following attributes:

- ``id``: ID of the examiner object in the database.
- ``user``: Object/map with the following attributes:
    - ``username``: (string)
    - ``email``: string
    - ``full_name``: string
"""
tags_docs = """List of objects/maps with the following attributes:

- ``id``: ID of the tag object in the database.
- ``tag``: string
"""
deadlines_docs = """List of objects/maps with the following attributes:

- ``id``: ID of the deadline object in the database.
- ``deadline`` (ISO datetime): The datetime when the delivery whas made.
"""


class ListOrCreateGroupRest(SelfdocumentingMixin, ListOrCreateModelView):
    resource = GroupResource
    form = GroupForm
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)

    def get_queryset(self):
        assignment_id = self.kwargs['assignment_id']
        qry = self.resource.model.objects.filter(parentnode=assignment_id)
        qry = qry.select_related('feedback')
        qry = qry.annotate(num_deliveries=Count('deadlines__deliveries'))
        qry = qry.prefetch_related('deadlines',
                                   'examiners', 'examiners__user',
                                   'examiners__user__devilryuserprofile',
                                   'candidates', 'candidates__student',
                                   'candidates__student__devilryuserprofile')
        qry = qry.order_by('id')
        return qry

    def get(self, request, assignment_id):
        """
        Returns a list with one object/map for each group in the assignment
        with the ``assignment_id`` specified in the URL. The dict has the
        following attributes:

        {responsetable}
        """
        return super(ListOrCreateGroupRest, self).get(request)

    def postprocess_get_docs(self, docs):
        help = {'id': {'help': 'ID the the group',
                       'meta': 'string'},
                'etag': {'help': 'ETAG changes each time the group is saved',
                         'meta': 'string'},
                'name': {'help': 'Name of the group',
                         'meta': 'string'},
                'is_open': {'help': 'Is the group open? (boolean)',
                            'meta': 'boolean'},
                'num_deliveries': {'help': 'Number of deliveries',
                            'meta': 'int'},
                'feedback': {'help': feedback_docs,
                            'meta': 'object or null'},
                'candidates': {'help': candidates_docs,
                            'meta': 'list'},
                'examiners': {'help': examiners_docs,
                            'meta': 'list'},
                'tags': {'help': tags_docs,
                            'meta': 'list'},
                'deadlines': {'help': deadlines_docs,
                            'meta': 'list'},
               }
        responsetable = self.html_create_attrtable(help)
        return docs.format(responsetable=responsetable)

    def post(self, request, assignment_id):
        data = self.CONTENT
        #print 'POST CONTENT:'
        #from pprint import pprint
        #pprint(data)
        #print
        manager = GroupManager(assignment_id)
        with transaction.commit_on_success():
            try:
                manager.update_group(name=data['name'],
                                     is_open=data['is_open'])
                manager.update_examiners(data['examiners'])
                manager.update_candidates(data['candidates'])
            except ValidationError, e:
                raise ValidationErrorResponse(e)
            else:
                return Response(201, manager.group)




class InstanceGroupRest(InstanceModelView):
    resource = GroupResource
    form = GroupForm
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)

    def _not_found_response(self, assignment_id, group_id):
            raise NotFoundError('Group with assignment_id={assignment_id} and id={group_id} not found'.format(**vars()))

    def get(self, request, assignment_id, group_id):
        return super(InstanceGroupRest, self).get(request, id=group_id)

    def put(self, request, assignment_id, group_id):
        data = self.CONTENT
        try:
            manager = GroupManager(assignment_id, group_id)
        except AssignmentGroup.DoesNotExist:
            self._not_found_response(assignment_id, group_id)
        with transaction.commit_on_success():
            try:
                manager.update_group(name=data['name'],
                                     is_open=data['is_open'])
                manager.update_examiners(data['examiners'])
                manager.update_candidates(data['candidates'])
            except ValidationError, e:
                raise ValidationErrorResponse(e)
            else:
                return Response(200, manager.group)
