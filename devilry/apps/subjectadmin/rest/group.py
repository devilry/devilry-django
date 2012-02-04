from devilry.rest.indata import indata
from devilry.rest.restbase import RestBase

from devilry.apps.core.models import Assignment

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
    def read(self, user, assignmentid):
        assignmentadmin_required(user, "i18n.permissiondenied", assignmentid)


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
