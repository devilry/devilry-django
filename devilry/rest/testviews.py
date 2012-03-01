"""
Views used by the test suite.
"""

from restbase import RestBase
from error import NotFoundError

class RestPolls(RestBase):
    def create(self, pollname, choices):
        return dict(created=pollname,
                    createdchoices=choices)

    def read(self, id, something='Hello world'):
        if id != '1':
            raise NotFoundError('rest.restviews.pollnotfound', pollid=id)
        return dict(id=id,
                    something=something)

    def update(self, id, pollname, choices):
        return dict(id=id,
                    updated=pollname,
                    updatedchoices=choices)

    def delete(self, id):
        return dict(id=id)

    def list(self, search=''):
        return dict(search=search)

    def batch(self, polls_to_update=[], polls_to_create=[], polls_to_delete=[]):
        return dict(polls_to_update=polls_to_update,
                    polls_to_create=polls_to_create,
                    polls_to_delete=polls_to_delete)
