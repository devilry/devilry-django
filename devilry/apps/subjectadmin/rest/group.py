from devilry.rest.indata import indata
from devilry.rest.restbase import RestBase

from devilry.apps.core.models import (Assignment,
                                      AssignmentGroup,
                                      AssignmentGroupTag,
                                      Candidate,
                                      Examiner,
                                      Deadline)
from errors import PermissionDeniedError



class AssignmentadminRequiredError(PermissionDeniedError):
    """
    Raised to signal that a subject admin is required for the given operation.
    """


def assignmentadmin_required(user, errormsg, *assignmentids):
    if user.is_superuser:
        return
    for assignmentid in assignmentids:
        if assignmentid == None:
            raise AssignmentadminRequiredError(errormsg)
        if Assignment.where_is_admin(user).filter(id=assignmentid).count() == 0:
            raise AssignmentadminRequiredError(errormsg)


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
                  'feedback__is_passing_grade', 'feedback__save_timestamp')
        groups = AssignmentGroup.objects.filter(parentnode=assignmentid).select_related('feedback').values(*fields)
        return groups

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

    def read(self, user, assignmentid):
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


class RestGroup(RestBase):
    def __init__(self, daocls=GroupDao, **basekwargs):
        super(RestGroup, self).__init__(**basekwargs)
        self.dao = daocls()

    @indata(id=int)
    def read(self, id):
        return self.dao.read(self.user, id)

    #@indata(short_name=unicode, long_name=unicode)
    #def create(self, short_name, long_name):
        #return self.todict(self.dao.create(self.user, short_name, long_name))

    #@indata(id=int, short_name=unicode, long_name=unicode)
    #def update(self, id, short_name, long_name):
        #return self.todict(self.dao.update(self.user, id, short_name, long_name))

    #@indata(id=int)
    #def list(self, id=None):
        #items = self._get_items(id)
        #return dict(
            #params=dict(
                #parentnode_id=id
            #),
            #links=self.get_links(id),
            #items=items,
            #total=len(items)
        #)

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

    #def get_links(self, id):
        #links = {}
        #if id:
            #links['node'] = self.geturl(id)
        #return links
