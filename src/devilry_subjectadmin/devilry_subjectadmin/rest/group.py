from django.db.models import Q
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
from devilry.apps.core.models import AssignmentGroupTag
from devilry.apps.core.models import Delivery

from .errors import ValidationErrorResponse
from .errors import NotFoundError
from .errors import BadRequestFieldError
from .auth import IsAssignmentAdmin
from .fields import ListOfDictField
from .fields import DictField
from .mixins import SelfdocumentingMixin
from .log import logger




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


form_examiners_help = r"""List of examiners (objects/maps) to apply to the
group. For new groups, this is simply a list of examiners to create. For
existing groups, this list is synced with the saved examiners. Each object in
the list has the following attributes:

- ``id``: If this is ``None/null``, we create a new examiner.
- ``user``: An object/map. If ``id`` is ``None/null``, we create a new examiner
  linked to the user identified by ``user['id']``.  The user object may also
  have other attributes, which will simply be ignored.
 
Any existing examiner not identified by their ``id`` in the list of examiners
is **REMOVED** from the group.

To sum it up in practical terms:

- _Add examiner_: Add something like this to the list: ``{'user': {'id': 10}}``
- _Remove examiner_: Update the group with an examiners-list where the examiner
  is not included.
- _Update examiner_: Not possible. Makes no sense since the only changable
  attribute of examiner is the user, and you should add an examiner instead of
  changing the user-link of an existing user.
"""

form_candidates_help = r"""List of candidates (objects/maps) to apply to the
group. For new groups, this is simply a list of candidates to create. For
existing groups, this list is synced with the saved candidates. Each object in
the list has the following attributes:

- ``id``: If this is ``None/null``, we create a new candidate.
- ``candidate_id``: Defaults to empty string if not supplied.
- ``user``: An object/map. If ``id`` is ``None/null``, we create a new
  candidate linked to the user identified by ``user['id']``. The user object
  may also have other attributes, which will simply be ignored.
 
Any existing candidate not identified by their ``id`` in the list of candidates
is **REMOVED** from the group.

To sum it up in practical terms:

- _Add candidate_: Add something like this to the list: ``{'user': {'id': 10}}``
- _Remove candidate_: Update the group with an candidates-list where the candidate
  is not included.
- _Update candidate_: Only the ``candidate_id`` can be changed. A minimal
  example: ``{'id': 1, 'candidate_id': 'secret'}``
"""

form_tags_help = r"""List of tags (maps/objects) to set on the group. Each
object in the list ha the following attributes:

- ``id``: Ignored (but allowed since list/get has it).
- ``tag`` (string): The tag.

Each time group is saved, all tags are deleted, and the tags in this attribute
is added.
"""




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

    def _serialize_tag(self, tag):
        return {'id': tag.id,
                'tag': tag.tag}

    def serialize_tags(self):
        return map(self._serialize_tag, self.group.tags.all())

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

    def _create_tag(self, tag):
        self.group.tags.create(tag=tag)

    def update_tags(self, tagdicts):
        AssignmentGroupTag.objects.filter(assignment_group=self.group).delete()
        for tagdict in tagdicts:
            self._create_tag(tag=tagdict['tag'])

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
        id = forms.IntegerField(required=False)
        tag = forms.CharField()

class CandidatesField(ListOfDictField):
    class Form(forms.Form):
        id = forms.IntegerField(required=False)
        candidate_id = forms.CharField(required=False)
        user = UserField(required=False)

#class DeadlinesField(ListOfDictField):
    #class Form(forms.Form):
        #deadline = forms.DateTimeField()

class ExaminersField(ListOfDictField):
    class Form(forms.Form):
        id = forms.IntegerField(required=False)
        user = UserField(required=False)

class GroupForm(forms.Form):
    id = forms.IntegerField(required=False)
    name = forms.CharField(required=False,
                           help_text='The name of the group (string)')
    is_open = forms.BooleanField(required=False,
                                 help_text='Is open? (boolean)')
    candidates = CandidatesField(required=False,
                                 help_text=form_candidates_help)
    examiners = ExaminersField(required=False,
                               help_text=form_examiners_help)
    tags = TagsField(required=False,
                     help_text=form_tags_help)


class GroupResource(ModelResource):
    model = AssignmentGroup
    fields = ('id', 'name', 'etag', 'is_open', 'num_deliveries',
              'parentnode', 'feedback',
              'deadlines', 'examiners', 'candidates', 'tags')

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

    def tags(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_tags()

    def examiners(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_examiners()

    def candidates(self, instance):
        if isinstance(instance, self.model):
            return GroupSerializer(instance).serialize_candidates()

    def validate_request(self, data, files=None):
        for ignorefield in ('feedback', 'deadlines', 'num_deliveries'):
            if ignorefield in data:
                del data[ignorefield]
        return super(GroupResource, self).validate_request(data, files)




class SelfdocumentingGroupApiMixin(SelfdocumentingMixin):
    def postprocess_docs(self, docs):
        response = {'id': {'help': 'ID the the group',
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
        responsetable = self.html_create_attrtable(response)
        parameterstable = self.htmlformat_parameters_from_form()
        return docs.format(responsetable=responsetable,
                           parameterstable=parameterstable)


class ListOrCreateGroupRest(SelfdocumentingGroupApiMixin, ListOrCreateModelView):
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

        querystring = self.request.GET.get('query', '')
        if len(querystring) > 0:
            qry = qry.filter(Q(candidates__student__username__icontains=querystring) |
                             Q(candidates__student__email__icontains=querystring) |
                             Q(candidates__student__devilryuserprofile__full_name__icontains=querystring) |
                             Q(tags__tag__icontains=querystring))

        qry = qry.order_by('id')
        return qry

    def validate_request(self, datalist, files=None):
        cleaned_datalist = []
        if isinstance(datalist, dict):
            datalist = [datalist]
        for data in datalist:
            cleaned_data = super(ListOrCreateGroupRest, self).validate_request(data)
            cleaned_datalist.append(cleaned_data)
        return cleaned_datalist


    def get(self, request, assignment_id):
        """
        Without the ``query`` parameter, list all groups.

        # Parameters
        Use the ``query`` parameter in the querystring to search for groups by:

        - Candidate full name
        - Candidate username
        - Candidate email
        - Tags

        Uses case-ignore-contains search.

        # Returns
        Returns a list with one object/map for each group in the assignment
        with the ``assignment_id`` specified in the URL. The object has the
        following attributes:

        {responsetable}
        """
        return super(ListOrCreateGroupRest, self).get(request)

    def post(self, request, assignment_id):
        """
        # Parameters
        {parameterstable}

        # Returns
        An object/map with the following attributes:
        {responsetable}
        """
        datalist = self.CONTENT
        manager = GroupManager(assignment_id)
        created_groups = []
        with transaction.commit_on_success():
            for data in datalist:
                try:
                    manager.update_group(name=data['name'],
                                         is_open=data['is_open'])
                    manager.update_examiners(data['examiners'])
                    manager.update_candidates(data['candidates'])
                    manager.update_tags(data['tags'])
                except ValidationError, e:
                    raise ValidationErrorResponse(e)
                else:
                    logger.info('User=%s created AssignmentGroup id=%s', self.user, manager.group.id)
                    created_groups.append(manager.group)
        return Response(201, created_groups)


    def _not_found_response(self, assignment_id, group_id):
        raise NotFoundError('Group with assignment_id={assignment_id} and id={group_id} not found'.format(**vars()))

    def put(self, request, assignment_id):
        datalist = self.CONTENT
        updated_groups = []
        with transaction.commit_on_success():
            for data in datalist:
                if data['id'] == None:
                    raise BadRequestFieldError('id', 'Required.')
                group_id = data['id']
                try:
                    manager = GroupManager(assignment_id, group_id)
                except AssignmentGroup.DoesNotExist:
                    self._not_found_response(assignment_id, group_id)
                try:
                    manager.update_group(name=data['name'],
                                         is_open=data['is_open'])
                    manager.update_examiners(data['examiners'])
                    manager.update_candidates(data['candidates'])
                    manager.update_tags(data['tags'])
                except ValidationError, e:
                    raise ValidationErrorResponse(e)
                else:
                    logger.info('User=%s updated AssignmentGroup id=%s', self.user, group_id)
                    updated_groups.append(manager.group)
            return Response(200, updated_groups)



#class InstanceGroupRest(SelfdocumentingGroupApiMixin, InstanceModelView):
    #resource = GroupResource
    #form = GroupForm
    #permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)

    #def _not_found_response(self, assignment_id, group_id):
        #raise NotFoundError('Group with assignment_id={assignment_id} and id={group_id} not found'.format(**vars()))

    #def get(self, request, assignment_id, group_id):
        #"""
        #Returns aggregated data for the requested AssignmentGroup and related data:

        #{responsetable}
        #"""
        #return super(InstanceGroupRest, self).get(request, id=group_id)

    #def put(self, request, assignment_id, group_id):
        #"""
        ## Parameters
        #{parameterstable}

        ## Returns (the same as GET)
        #An object/map with the following attributes:
        #{responsetable}
        #"""
        #data = self.CONTENT
        #try:
            #manager = GroupManager(assignment_id, group_id)
        #except AssignmentGroup.DoesNotExist:
            #self._not_found_response(assignment_id, group_id)
        #with transaction.commit_on_success():
            #try:
                #manager.update_group(name=data['name'],
                                     #is_open=data['is_open'])
                #manager.update_examiners(data['examiners'])
                #manager.update_candidates(data['candidates'])
                #manager.update_tags(data['tags'])
            #except ValidationError, e:
                #raise ValidationErrorResponse(e)
            #else:
                #logger.info('User=%s updated AssignmentGroup id=%s', self.user, group_id)
                #return Response(200, manager.group)
