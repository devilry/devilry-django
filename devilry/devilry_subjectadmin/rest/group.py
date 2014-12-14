from django.db.models import Q
from django.db import transaction
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _

from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import Response
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView
from devilry.apps.core.models.deliverytypes import NON_ELECTRONIC
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import AssignmentGroupTag
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import Assignment
from .errors import ValidationErrorResponse
from .errors import NotFoundError
from .errors import BadRequestFieldError
from .errors import PermissionDeniedError
from .auth import IsAssignmentAdmin
from .fields import ListOfDictField
from .fields import DictField
from devilry.devilry_subjectadmin.rest.mixins import SelfdocumentingMixin
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
                    'delivery_id': feedback.delivery.id,
                    'points': feedback.points,
                    'is_passing_grade': feedback.is_passing_grade,
                    'save_timestamp': feedback.save_timestamp}
        else:
            return None

    def _serialize_user(self, user):
        full_name = user.devilryuserprofile.full_name
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'displayname': full_name or user.username,
                'full_name': full_name}

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
    def __init__(self, user, assignment=None, group=None, createmode=False, usercache=None):
        self.user = user
        self.createmode = createmode
        self.usercache = usercache
        if group:
            self.group = group
        elif assignment:
            self.group = AssignmentGroup(parentnode=assignment)
        else:
            raise ValueError('One of assignment or group must be supplied.')
        self.serializer = GroupSerializer(self.group)

    def get_group_from_db(self):
        return AssignmentGroup.objects.get(id=self.group.id)

    def update_group(self, name, is_open):
        self.group.name = name
        self.group.is_open = is_open
        self.group.save()

    def create_first_deadline_if_available(self):
        assignment = self.group.parentnode
        first_deadline = assignment.first_deadline
        if first_deadline and assignment.delivery_types != NON_ELECTRONIC:
            self.group.deadlines.create(deadline=first_deadline)

    def _create_tag(self, tag):
        self.group.tags.create(tag=tag)

    def update_tags(self, tagdicts):
        if not self.createmode:
            AssignmentGroupTag.objects.filter(assignment_group=self.group).delete()
        for tagdict in tagdicts:
            self._create_tag(tag=tagdict['tag'])

    def _get_user(self, user_id):
        if self.usercache != None:
            try:
                return self.usercache[user_id]
            except KeyError:
                pass
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist, e:
            raise ValidationError('User with ID={0} does not exist'.format(user_id))
        else:
            if self.usercache:
                self.usercache[user_id] = user
            return user

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
        if not self.createmode:
            to_delete = {}
            for examiner in self.group.examiners.all():
                to_delete[examiner.id] = examiner
        for examinerdict in examinerdicts:
            examiner_id = examinerdict['id']
            isnew = examiner_id == None
            if isnew:
                user_id = examinerdict['user']['id']
                self._create_examiner(user_id)
            elif self.createmode:
                raise ValueError('Can not update examiners when createmode=True.')
            else:
                # Can not change existing examiners, only delete them
                del to_delete[examiner_id] # Remove existing from to_delete (thus, to_delete will be correct after the loop)
        if not self.createmode:
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
        if not self.createmode:
            existing_by_id = {}
            for candidate in self.group.candidates.all():
                existing_by_id[candidate.id] = candidate
        for candidatedict in candidatedicts:
            id = candidatedict['id']
            isnew = id == None
            if isnew:
                user_id = candidatedict['user']['id']
                candidate_id = candidatedict['candidate_id']
                self._create_candidate(user_id=user_id, candidate_id=candidate_id)
            elif self.createmode:
                raise ValueError('Can not update candidates when createmode=True.')
            else:
                existing_candidate = existing_by_id[id]
                self._update_candate(existing_candidate, candidatedict['candidate_id'])
                del existing_by_id[id] # Remove existing from existing_by_id (which becomes to_delete) (thus, to_delete will be correct after the loop)
        if not self.createmode:
            to_delete = existing_by_id
            if len(to_delete) > 0:
                if self.group.can_delete(self.user):
                    for candidate in to_delete.itervalues():
                        candidate.delete()
                else:
                    raise PermissionDeniedError('You do not have permission to remove students from this group. Only superusers can remove students from groups with deliveries.')

    def delete(self):
        if self.group.can_delete(self.user):
            self.group.delete()
        else:
            raise PermissionDeniedError('You do not have permission to delete this group. Only superusers can delete groups with deliveries.')




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
              'parentnode', 'feedback', 'status',
              'deadlines', 'examiners', 'candidates', 'tags')

    def serialize_model(self, instance):
        data = super(GroupResource, self).serialize_model(instance)
        if not 'num_deliveries' in data:
            # This is used when working directly with the instance. The listing
            # (query) annotates this field instead of querying for each object
            data['num_deliveries'] = Delivery.objects.filter(deadline__assignment_group=instance).count()
        return data

    def status(self, instance):
        if isinstance(instance, self.model):
            return instance.get_status()

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
        qry = qry.prefetch_related(
            'deadlines',
            'tags',
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

        **NOTE**: If the assignment has ``first_deadline`` set, the deadline will be created.
        This will set ``is_open`` to ``true`` even if the ``is_open``-parameter
        is set to ``false``. We have not made a workaround for this, since setting
        ``is_open=False`` when creating a group have no know use-cases, and a workaround
        would require one extra save.

        # Returns
        An object/map with the following attributes:
        {responsetable}
        """
        datalist = self.CONTENT
        created_groups = []
        usercache = {}

        try:
            assignment = Assignment.objects.filter(id=assignment_id)\
                    .select_related(
                            'parentnode',
                            'parentnode__parentnode')\
                    .prefetch_related(
                            'admins',
                            'parentnode__admins',
                            'parentnode__parentnode__admins'
                            )\
                    .get()
        except Assignment.DoesNotExist:
            raise NotFoundError('No assignment with ID={} exists.'.format(assignment_id))

        with transaction.commit_on_success():
            for data in datalist:
                try:
                    manager = GroupManager(request.user, assignment, createmode=True, usercache={})
                    manager.update_group(name=data['name'],
                                         is_open=data['is_open'])
                    manager.create_first_deadline_if_available()
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


    def _update_examinersonly(self, manager, data):
        manager.update_examiners(data['examiners'])

    def _update_tagsonly(self, manager, data):
        manager.update_tags(data['tags'])

    def _update_all(self, manager, data):
        manager.update_group(name=data['name'],
                             is_open=data['is_open'])
        manager.update_examiners(data['examiners'])
        manager.update_candidates(data['candidates'])
        manager.update_tags(data['tags'])

    def _query_groups_by_id(self, groupids):
        qry = AssignmentGroup.objects.filter(id__in=groupids)
        qry = qry.select_related('feedback')
        qry = qry.prefetch_related(
            'deadlines',
            'tags',
            'examiners', 'examiners__user',
            'examiners__user__devilryuserprofile',
            'candidates', 'candidates__student',
            'candidates__student__devilryuserprofile')
        return qry.all()

    def put(self, request, assignment_id):
        if request.META.get('X_DEVILRY_DELETEHACK'):
            # NOTE: This is only a workaround for the limitations of the Django test client in version 1.4. DELETE with request data is supported in 1.5.
            return self.delete(request, assignment_id)

        examinersOnly = request.GET.get('examinersOnly') == 'true'
        tagsOnly = request.GET.get('tagsOnly') == 'true'
        if examinersOnly and tagsOnly:
            raise BadRequestFieldError('examinersOnly', 'You can only set one of these to true: examinersOnly and tagsOnly.')
        if examinersOnly:
            update_method = self._update_examinersonly
        elif tagsOnly:
            update_method = self._update_tagsonly
        else:
            update_method = self._update_all

        datalist = self.CONTENT
        updated_groups = []
        usercache = {} # Internal cache to avoid looking up the same users multiple times
        groupids = []
        data_by_groupid = {}
        for data in datalist:
            if data['id'] == None:
                raise BadRequestFieldError('id', 'Required.')
            group_id = data['id']
            groupids.append(group_id)
            data_by_groupid[group_id] = data
        groups = self._query_groups_by_id(groupids)
        if len(groups) != len(datalist):
            raise NotFoundError('One or more of the requested groups does not exist.'.format(**vars()))
        with transaction.commit_on_success():
            for group in groups:
                manager = GroupManager(request.user, assignment_id, group=group, usercache=usercache)
                try:
                    update_method(manager, data_by_groupid[group.id])
                except ValidationError, e:
                    raise ValidationErrorResponse(e)
                else:
                    logger.info('User=%s updated AssignmentGroup id=%s', self.user, group.id)
                    updated_groups.append(manager.group.id)
            return Response(200, self._query_groups_by_id(updated_groups))

    def delete(self, request, assignment_id):
        datalist = self.CONTENT

        groupids = []
        for data in datalist:
            if data['id'] == None:
                raise BadRequestFieldError('id', 'Required.')
            group_id = data['id']
            groupids.append(group_id)

        groups = self._query_groups_by_id(groupids)
        if len(groups) != len(datalist):
            raise NotFoundError('One or more of the requested groups does not exist.'.format(**vars()))
        with transaction.commit_on_success():
            for group in groups:
                manager = GroupManager(request.user, assignment_id, group)
                try:
                    manager.delete()
                except ValidationError, e:
                    raise ValidationErrorResponse(e)
                else:
                    logger.warning('User=%s deleted AssignmentGroup id=%s', self.user, group.id)
            return Response(204, '')
