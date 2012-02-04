from devilry.rest.indata import indata
from devilry.rest.restbase import RestBase

from devilry.apps.core.models import (Assignment,
                                      AssignmentGroup,
                                      AssignmentGroupTag
                                     )

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
    - deadlines
    - feedback
    - tags
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
        return group

    def _convert_groupslist_to_groupsdict(self, groups):
        groupsdict = {}
        for group in groups:
            groupsdict[group['id']] = self._prepare_group(group)
        return groupsdict

    def _merge_tags_with_groupsdict(self, tags, groupsdict):
        for tagdict in tags:
            group = groupsdict[tagdict['assignment_group_id']]
            group['tags'].append(tagdict['tag'])

    def read(self, user, assignmentid):
        assignmentadmin_required(user, "i18n.permissiondenied", assignmentid)
        groups = self._get_groups(assignmentid)
        groupsdict = self._convert_groupslist_to_groupsdict(groups)

        tags = AssignmentGroupTag.objects.filter(assignment_group__parentnode=assignmentid).values('assignment_group_id', 'tag')
        self._merge_tags_with_groupsdict(tags, groupsdict)
        for group in groupsdict.itervalues():
            print group


#class Group(RestBase):
    #def __init__(self, daocls=NodeDao, **basekwargs):
        #super(Group, self).__init__(**basekwargs)
        #self.dao = daocls()

    #def todict(self, node):
        #item = node
        #links = {}
        #links['toplevel-nodes'] = self.geturl()
        #if node['parentnode_id'] != None:
            #links['parentnode'] = self.geturl(node['parentnode_id'])
        #links['childnodes'] = self.geturl(params={'id': node['id']})
        #links['node'] = self.geturl(node['id'])
        #return dict(
            #item=item,
            #links=links
        #)

    #@indata(id=int)
    #def read(self, id):
        #return self.todict(self.dao.read(self.user, id))

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
