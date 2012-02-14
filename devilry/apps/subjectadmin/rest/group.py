from devilry.rest.indata import indata
from devilry.rest.restbase import RestBase
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from devilry.apps.core.models import (AssignmentGroup,
                                      AssignmentGroupTag,
                                      Candidate,
                                      Examiner,
                                      Deadline)
#from devilry.rest.indata import none_or_bool
#from devilry.rest.indata import none_or_unicode
from devilry.rest.indata import isoformatted_datetime
from auth import assignmentadmin_required



#def _require_list_of_students(value):
    #return value

#def _require_list_of_examiner(value):
    #return value

#def _require_list_of_tags(value):
    #return value

#def _require_list_of_deadlines(value):
    #return value



class GroupDao(object):
    """
    Makes it convenient to work with everything related to an AssignmentGroup:

    - name
    - is_open
    - feedback
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

    def _get_groups(self, assignmentid):
        """
        Get a list of group dictionaries.
        """
        fields = ('id', 'name', 'is_open', 'feedback__grade', 'feedback__points',
                  'feedback__is_passing_grade', 'feedback__save_timestamp',
                  'num_deliveries')
        qry = AssignmentGroup.objects.filter(parentnode=assignmentid)
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

    def _merge_with_groupsdict(self, groupsdict, listofdicts, targetkey, assignmentgroup_key='assignment_group_id'):
        for dct in listofdicts:
            group = groupsdict[dct[assignmentgroup_key]]
            del dct[assignmentgroup_key]
            group[targetkey].append(dct)

    def _get_candidates(self, assignmentid):
        fields = ('assignment_group_id', 'candidate_id',
                  'student__username', 'student__email',
                  'student__devilryuserprofile__full_name')
        return Candidate.objects.filter(assignment_group__parentnode=assignmentid).values(*fields)

    def _get_examiners(self, assignmentid):
        fields = ('assignmentgroup_id',
                  'user__username', 'user__email',
                  'user__devilryuserprofile__full_name')
        return Examiner.objects.filter(assignmentgroup__parentnode=assignmentid).values(*fields)

    def _get_tags(self, assignmentid):
        fields = ('assignment_group_id', 'tag')
        return AssignmentGroupTag.objects.filter(assignment_group__parentnode=assignmentid).values(*fields)

    def _get_deadlines(self, assignmentid):
        fields = ('assignment_group_id', 'deadline')
        return Deadline.objects.filter(assignment_group__parentnode=assignmentid).values(*fields)

    def _merge(self, groups, candidates, examiners, tags, deadlines):
        groupsdict = self._convert_groupslist_to_groupsdict(groups)
        self._merge_with_groupsdict(groupsdict, candidates, 'students')
        self._merge_with_groupsdict(groupsdict, examiners, 'examiners', assignmentgroup_key='assignmentgroup_id')
        self._merge_with_groupsdict(groupsdict, tags, 'tags')
        self._merge_with_groupsdict(groupsdict, deadlines, 'deadlines')
        return groupsdict.values()

    def list(self, user, assignmentid):
        """
        Returns a list of one dict for each group in the assignment with the
        given ``assignmentid``. The dict has the following keys:

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
        assignmentadmin_required(user, "i18n.permissiondenied", assignmentid)
        groups = self._get_groups(assignmentid)
        candidates = self._get_candidates(assignmentid)
        examiners = self._get_examiners(assignmentid)
        tags = self._get_tags(assignmentid)
        deadlines = self._get_deadlines(assignmentid)
        groups = self._merge(groups, candidates, examiners, tags, deadlines)
        return groups


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

    def _create_from_singlekey_dict(self, modelcls, group, examinerdict, key,
                                    objectattr, getvalue=lambda v: v,
                                   assignmentgroupattr='assignment_group'):
        typename = modelcls.__class__.__name__
        if not isinstance(examinerdict, dict):
            raise ValueError('Each entry in the {typename} list must be a dict. '
                             'Given type: {giventypename}.'.format(typename=typename,
                                                                   giventypename=type(examinerdict)))
        try:
            value = examinerdict[key]
        except KeyError, e:
            raise ValueError('A {typename} dict must contain {key}. '
                             'Keys in the given dict: {keys}.'.format(typename=typename,
                                                                      key=key,
                                                                      keys=','.join(examinerdict.keys())))
        else:
            obj = modelcls()
            setattr(obj, assignmentgroupattr, group)
            setattr(obj, objectattr, getvalue(value))
            obj.save()
            return obj

    def _create_examiner_from_examinerdict(self, group, examinerdict):
        return self._create_from_singlekey_dict(Examiner, group, examinerdict,
                                                'user__username', 'user',
                                                assignmentgroupattr='assignmentgroup',
                                                getvalue=self._get_user)

    def _create_tag_from_tagdict(self, group, tagdict):
        return self._create_from_singlekey_dict(AssignmentGroupTag, group, tagdict, 'tag', 'tag')

    def _create_deadline_from_deadlinedict(self, group, deadlinedict):
        return self._create_from_singlekey_dict(Deadline, group, deadlinedict,
                                                'deadline', 'deadline',
                                                getvalue=isoformatted_datetime)


    def create_noauth(self, assignment, name=None, is_open=None,
                      students=[], examiners=[], tags=[], deadlines=[]):
        group = AssignmentGroup(parentnode=assignment)
        self._setattr_if_not_none(group, 'name', name)
        self._setattr_if_not_none(group, 'is_open', is_open)
        group.save()
        for studentdict in students:
            self._create_candidate_from_studentdict(group, studentdict)
        for examinerdict in examiners:
            self._create_examiner_from_examinerdict(group, examinerdict)
        return group



class RestGroup(RestBase):
    def __init__(self, daocls=GroupDao, **basekwargs):
        super(RestGroup, self).__init__(**basekwargs)
        self.dao = daocls()

    @indata(assignmentid=int)
    def list(self, assignmentid):
        return self.dao.list(self.user, assignmentid)

    #@indata(name=none_or_unicode,
            #is_open=none_or_bool,
            #students=require_list_of_students,
            #examiners=require_list_of_examiner,
            #tags=require_list_of_tags,
            #deadlines=require_list_of_deadlines)
    #def create(self, name='', is_open=True, students=[], examiners=[], tags=[], deadlines=[]):
        #pass

    #@indata(id=int, short_name=unicode, long_name=unicode)
    #def update(self, id, short_name, long_name):
        #return self.todict(self.dao.update(self.user, id, short_name, long_name))

    ##    @indata(parentnode_id=force_list)
##    def batch(self, create=[], update=[], delete=[]):
##        for kw in create:
##            self.create(**kw)
##        for kw in update:
##            self.update(**kw)
##        for kw in delete:
##            self.delete(**kw)

    #def _get_items(self, parentnode_id):
        #return [self.todict(item) for item in self.dao.list(self.user, parentnode_id)]

