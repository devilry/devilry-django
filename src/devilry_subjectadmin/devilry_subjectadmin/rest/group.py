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
from auth import IsAssignmentAdmin
from fields import ListOfDictField


class IsAssignmentAdminAssignmentIdKwarg(IsAssignmentAdmin):
    ID_KWARG = 'assignment_id'


class GroupDao(object):
    def _setattr_if_not_none(self, obj, attrname, value):
        if value != None:
            setattr(obj, attrname, value)

    def _get_user(self, username):
        try:
            return User.objects.get(username=username)
        except ObjectDoesNotExist, e:
            raise ValueError('User does not exist: {0}'.format(username))

    def _create_candidate_from_studentdict(self, group, studentdict):
        if not isinstance(studentdict, dict):
            raise ValueError('Each entry in the students list must be a dict. '
                             'Given type: {0}.'.format(type(studentdict)))
        try:
            username = studentdict['student__username']
        except KeyError, e:
            raise ValueError('A student dict must contain student__username. '
                             'Keys in the given dict: {0}.'.format(','.join(studentdict.keys())))
        else:
            candidate_id = studentdict.get('candidate_id')
            candidate = Candidate(assignment_group=group,
                                  student=self._get_user(username),
                                  candidate_id=candidate_id)
            candidate.save()
            return candidate

    def _create_from_singlekey_dict(self, modelcls, group, singlekeydict, key,
                                    objectattr, getvalue=lambda v: v,
                                    assignmentgroupattr='assignment_group'):
        typename = modelcls.__class__.__name__
        if not isinstance(singlekeydict, dict):
            raise ValueError('Each entry in the {typename} list must be a dict. '
                             'Given type: {giventypename}.'.format(typename=typename,
                                                                   giventypename=type(singlekeydict)))
        try:
            value = singlekeydict[key]
        except KeyError, e:
            raise ValueError('A {typename} dict must contain {key}. '
                             'Keys in the given dict: {keys}.'.format(typename=typename,
                                                                      key=key,
                                                                      keys=','.join(singlekeydict.keys())))
        else:
            obj = modelcls()
            setattr(obj, assignmentgroupattr, group)
            setattr(obj, objectattr, getvalue(value))
            obj.save()
            return obj

    def _create_examiner_from_examinerdict(self, group, examinerdict):
        user = User.objects.get(id=examinerdict.get('user_id'))
        examiner = Examiner(user=user, assignmentgroup=group)
        examiner.save()
        return examiner

    def _create_tag_from_tagdict(self, group, tagdict):
        return self._create_from_singlekey_dict(AssignmentGroupTag, group, tagdict, 'tag', 'tag')

    def _create_deadline_from_deadlinedict(self, group, deadlinedict):
        return self._create_from_singlekey_dict(Deadline, group, deadlinedict,
                                                'deadline', 'deadline')


    def create(self, assignment_id, name=None, is_open=None,
                      students=[], examiners=[], tags=[], deadlines=[]):
        group = AssignmentGroup(parentnode_id=assignment_id)
        self._setattr_if_not_none(group, 'name', name)
        self._setattr_if_not_none(group, 'is_open', is_open)
        group.save()
        for studentdict in students:
            self._create_candidate_from_studentdict(group, studentdict)
        for examinerdict in examiners:
            self._create_examiner_from_examinerdict(group, examinerdict)
        for tagdict in tags:
            self._create_tag_from_tagdict(group, tagdict)
        for deadlinedict in deadlines:
            self._create_deadline_from_deadlinedict(group, deadlinedict)
        return group



class GroupListingAggregator(object):
    """
    Aggregates AssignmentGroup and related data:

    - name
    - Active feedback
    - tags
    - deadlines
    - Candidates (students)
        - Candidate ID
        - Username
        - Full name
        - Email
    - Examiners
        - Username
        - Full name
        - Email
    """

    def _get_groups(self, assignment_id):
        """
        Get a list of group dictionaries.
        """
        fields = ('id', 'name', 'is_open', 'feedback__grade', 'feedback__points',
                  'feedback__is_passing_grade', 'feedback__save_timestamp',
                  'num_deliveries')
        qry = AssignmentGroup.objects.filter(parentnode=assignment_id)
        qry = qry.select_related('feedback')
        qry = qry.annotate(num_deliveries=Count('deadlines__deliveries'))
        return qry.values(*fields)

    def _prepare_group(self, group):
        """ Add the separate-query-aggreagated fields to the group dict. """
        group['tags'] = []
        group['students'] = []
        group['examiners'] = []
        group['deadlines'] = []
        return group

    def _convert_groupslist_to_groupsdict(self, groups):
        groupsdict = {}
        for group in groups:
            groupsdict[group['id']] = self._prepare_group(group)
        return groupsdict

    def _merge_with_groupsdict(self, groupsdict, listofdicts, targetkey,
                               assignmentgroup_key='assignment_group_id'):
        for dct in listofdicts:
            group = groupsdict[dct[assignmentgroup_key]]
            del dct[assignmentgroup_key]
            group[targetkey].append(dct)

    def _merge_examiners_with_groupsdict(self, groupsdict, examiners):
        for examinerdct in examiners:
            group = groupsdict[examinerdct['assignmentgroup_id']]
            group['examiners'].append({'id': examinerdct.get('id'),
                                       'user_id': examinerdct.get('user__id'),
                                       'username': examinerdct.get('user__username'),
                                       'full_name': examinerdct.get('user__devilryuserprofile__full_name'),
                                       'email': examinerdct.get('user__email')})

    def _get_candidates(self, assignment_id):
        fields = ('assignment_group_id', 'candidate_id',
                  'student__username', 'student__email',
                  'student__devilryuserprofile__full_name')
        return Candidate.objects.filter(assignment_group__parentnode=assignment_id).values(*fields)

    def _get_examiners(self, assignment_id):
        fields = ('assignmentgroup_id', 'id',
                  'user__id', 'user__username', 'user__email',
                  'user__devilryuserprofile__full_name')
        return Examiner.objects.filter(assignmentgroup__parentnode=assignment_id).values(*fields)

    def _get_tags(self, assignment_id):
        fields = ('assignment_group_id', 'tag')
        return AssignmentGroupTag.objects.filter(assignment_group__parentnode=assignment_id).values(*fields)

    def _get_deadlines(self, assignment_id):
        fields = ('assignment_group_id', 'deadline')
        return Deadline.objects.filter(assignment_group__parentnode=assignment_id).values(*fields)

    def _merge(self, groups, candidates, examiners, tags, deadlines):
        groupsdict = self._convert_groupslist_to_groupsdict(groups)
        self._merge_with_groupsdict(groupsdict, candidates, 'students')
        #self._merge_with_groupsdict(groupsdict, examiners, 'examiners', assignmentgroup_key='assignmentgroup_id')
        self._merge_with_groupsdict(groupsdict, tags, 'tags')
        self._merge_with_groupsdict(groupsdict, deadlines, 'deadlines')
        self._merge_examiners_with_groupsdict(groupsdict, examiners)
        return groupsdict.values()

    def list(self, assignment_id):
        """
        Returns a list of one dict for each group in the assignment with the
        given ``assignment_id``. The dict has the following keys:

        - name --- string
        - is_open --- boolean
        - feedback__grade --- string
        - feedback__points --- int
        - feedback__save_timestamp --- datetime
        - feedback__is_passing_grade --- boolean
        - students --- list of dicts with the following keys:
            - candidate_id --- string
            - student__username --- string
            - student__email --- string
            - student__devilryuserprofile__full_name --- string
        - examiners --- list of dicts with the following keys:
            - user__username --- string
            - user__devilryuserprofile__full_name --- string
            - user__email --- string
        - tags --- list of dicts with the following keys:
            - tag --- string
        - deadlines --- list of dicts with the following keys:
            - deadline --- datetime
        """
        groups = self._get_groups(assignment_id)
        candidates = self._get_candidates(assignment_id)
        examiners = self._get_examiners(assignment_id)
        tags = self._get_tags(assignment_id)
        deadlines = self._get_deadlines(assignment_id)
        groups = self._merge(groups, candidates, examiners, tags, deadlines)
        return groups


    def tull(self, assignment_id):
        qry = AssignmentGroup.objects.filter(parentnode=assignment_id)
        qry = qry.select_related('feedback')
        qry = qry.annotate(num_deliveries=Count('deadlines__deliveries'))
        qry = qry.prefetch_related('deadlines')
        return qry




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
    tags = TagsField(required=False)
    students = StudentsField(required=False)
    deadlines = DeadlinesField(required=False)
    examiners = ExaminersField(required=False)



class SubjectListOrCreateGroupResource(ModelResource):
    model = AssignmentGroup
    fields = ('id', 'name', 'etag', 'is_open', 'num_deliveries',
              'parentnode', 'feedback', 'deadlines', 'examiners', 'candidates')

    def parentnode(self, instance):
        if isinstance(instance, self.model):
            return instance.parentnode_id

    def feedback(self, instance):
        if isinstance(instance, self.model):
            feedback = instance.feedback
            return {'id': feedback.id,
                    'grade': feedback.grade,
                    'points': feedback.points,
                    'is_passing_grade': feedback.is_passing_grade,
                    'save_timestamp': feedback.save_timestamp}

    def deadlines(self, instance):
        if isinstance(instance, self.model):
            def to_dict(deadline):
                return {'id': deadline.id,
                        'deadline': deadline.deadline}
            return map(to_dict, instance.deadlines.all())

    def _create_userdict(self, user):
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.devilryuserprofile.full_name}

    def examiners(self, instance):
        if isinstance(instance, self.model):
            def to_dict(examiner):
                return {'id': examiner.id,
                        'user': self._create_userdict(examiner.user)}
            return map(to_dict, instance.examiners.all())

    def candidates(self, instance):
        if isinstance(instance, self.model):
            def to_dict(candidate):
                return {'id': candidate.id,
                        'candidate_id': candidate.candidate_id,
                        'user': self._create_userdict(candidate.student)}
            return map(to_dict, instance.candidates.all())




class ListOrCreateGroupRest(ListOrCreateModelView):
    resource = SubjectListOrCreateGroupResource
    #form = PostForm
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
        return qry

    def get(self, request, assignment_id):
        """
        Returns a list of one dict for each group in the assignment with the
        given ``assignment_id``. The dict has the following keys:

        - id --- int
        - etag --- string
        - name --- string
        - is_open --- boolean
        - num_deliveries --- Number of deliveries
        - feedback --- active feedback
            - grade --- string
            - points --- int
            - save_timestamp --- datetime
            - is_passing_grade --- boolean
        - students --- list of dicts with the following keys:
            - id
            - candidate_id --- string
            - username --- string
            - email --- string
            - devilryuserprofile__full_name --- string
        - examiners --- list of dicts with the following keys:
            - id
            - username --- string
            - devilryuserprofile__full_name --- string
            - email --- string
        - tags --- list of dicts with the following keys:
            - id
            - tag --- string
        - deadlines --- list of dicts with the following keys:
            - id
            - deadline --- datetime
        """
        return super(ListOrCreateGroupRest, self).get(request)

    #def post(self, request, assignment_id):
        #group = self.dao.create(assignment_id, **self.CONTENT)
        #return Response(201, dict(id=group.id))




class InstanceGroupRest(View):
    resource = FormResource
    form = PostForm
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)
    def __init__(self, daocls=GroupDao):
        self.dao = daocls()

    #def get(self):

    def put(self, request, assignment_id, group_id):
        group = self.dao.update(**self.CONTENT)
        return group.id
