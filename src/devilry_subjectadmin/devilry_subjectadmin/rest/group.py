from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import Response
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView
from django import forms

from devilry.apps.core.models import (AssignmentGroup,
                                      AssignmentGroupTag,
                                      Candidate,
                                      Examiner,
                                      Deadline)
from .auth import IsAssignmentAdmin
from .fields import ListOfDictField
from .mixins import SelfdocumentingMixin


class IsAssignmentAdminAssignmentIdKwarg(IsAssignmentAdmin):
    ID_KWARG = 'assignment_id'



class GroupSerializer(object):
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


class GroupCreator(object):
    def __init__(self, assignment_id):
        self.assignment_id = assignment_id
        self.group = self.get_group()

    def get_group(self):
        return AssignmentGroup()

    def update_group(self, name, is_open):
        self.group.name = name
        self.group.is_open = is_open
        self.group.save()

    #def update_examiners(self, examiners):
        #for existing_examiner in self.group.examiners.all():

    #def _setattr_if_not_none(self, obj, attrname, value):
        #if value != None:
            #setattr(obj, attrname, value)

    #def _get_user(self, username):
        #try:
            #return User.objects.get(username=username)
        #except ObjectDoesNotExist, e:
            #raise ValueError('User does not exist: {0}'.format(username))

    #def _create_candidate_from_studentdict(self, group, studentdict):
        #if not isinstance(studentdict, dict):
            #raise ValueError('Each entry in the students list must be a dict. '
                             #'Given type: {0}.'.format(type(studentdict)))
        #try:
            #username = studentdict['student__username']
        #except KeyError, e:
            #raise ValueError('A student dict must contain student__username. '
                             #'Keys in the given dict: {0}.'.format(','.join(studentdict.keys())))
        #else:
            #candidate_id = studentdict.get('candidate_id')
            #candidate = Candidate(assignment_group=group,
                                  #student=self._get_user(username),
                                  #candidate_id=candidate_id)
            #candidate.save()
            #return candidate

    #def _create_from_singlekey_dict(self, modelcls, group, singlekeydict, key,
                                    #objectattr, getvalue=lambda v: v,
                                    #assignmentgroupattr='assignment_group'):
        #typename = modelcls.__class__.__name__
        #if not isinstance(singlekeydict, dict):
            #raise ValueError('Each entry in the {typename} list must be a dict. '
                             #'Given type: {giventypename}.'.format(typename=typename,
                                                                   #giventypename=type(singlekeydict)))
        #try:
            #value = singlekeydict[key]
        #except KeyError, e:
            #raise ValueError('A {typename} dict must contain {key}. '
                             #'Keys in the given dict: {keys}.'.format(typename=typename,
                                                                      #key=key,
                                                                      #keys=','.join(singlekeydict.keys())))
        #else:
            #obj = modelcls()
            #setattr(obj, assignmentgroupattr, group)
            #setattr(obj, objectattr, getvalue(value))
            #obj.save()
            #return obj

    #def _create_examiner_from_examinerdict(self, group, examinerdict):
        #user = User.objects.get(id=examinerdict.get('user_id'))
        #examiner = Examiner(user=user, assignmentgroup=group)
        #examiner.save()
        #return examiner

    #def _create_tag_from_tagdict(self, group, tagdict):
        #return self._create_from_singlekey_dict(AssignmentGroupTag, group, tagdict, 'tag', 'tag')

    #def _create_deadline_from_deadlinedict(self, group, deadlinedict):
        #return self._create_from_singlekey_dict(Deadline, group, deadlinedict,
                                                #'deadline', 'deadline')


    #def create(self, assignment_id, name, is_open,
               #students=[], examiners=[], tags=[], deadlines=[]):
        #group = AssignmentGroup(parentnode_id=assignment_id,
                                #name=name, is_open=is_open)
        #group.save()
        ##for studentdict in students:
            ##self._create_candidate_from_studentdict(group, studentdict)
        ##for examinerdict in examiners:
            ##self._create_examiner_from_examinerdict(group, examinerdict)
        ##for tagdict in tags:
            ##self._create_tag_from_tagdict(group, tagdict)
        ##for deadlinedict in deadlines:
            ##self._create_deadline_from_deadlinedict(group, deadlinedict)
        #return group




class TagsField(ListOfDictField):
    class Form(forms.Form):
        tag = forms.CharField()

class StudentsField(ListOfDictField):
    class Form(forms.Form):
        candidate_id = forms.CharField()
        student__username = forms.CharField()
        student__email = forms.CharField()
        student__devilryuserprofile__full_name = forms.CharField()

class DeadlinesField(ListOfDictField):
    class Form(forms.Form):
        deadline = forms.DateTimeField()

class ExaminersField(ListOfDictField):
    class Form(forms.Form):
        id = forms.IntegerField()
        user_id = forms.IntegerField()
        username = forms.CharField()
        email = forms.CharField()
        devilryuserprofile__full_name = forms.CharField()

class PostForm(forms.Form):
    name = forms.CharField(required=False)
    is_open = forms.BooleanField(required=False)
    #tags = TagsField(required=False)
    #students = StudentsField(required=False)
    #deadlines = DeadlinesField(required=False)
    #examiners = ExaminersField(required=False)


class ListOrCreateGroupResource(ModelResource):
    model = AssignmentGroup
    fields = ('id', 'name', 'etag', 'is_open', 'num_deliveries',
              'parentnode', 'feedback', 'deadlines', 'examiners', 'candidates')

    def parentnode(self, instance):
        if isinstance(instance, self.model):
            return instance.parentnode_id

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
    resource = ListOrCreateGroupResource
    form = PostForm
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
        group = self.dao.create(assignment_id, **self.CONTENT)
        return Response(201, dict(id=group.id))




class InstanceGroupRest(View):
    resource = FormResource
    form = PostForm
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)

    def put(self, request, assignment_id, group_id):
        #group = self.dao.update(**self.CONTENT)
        #return group.id
        pass
