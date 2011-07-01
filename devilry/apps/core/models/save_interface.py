from django.contrib.auth.models import User

class SaveInterface(object):
    def can_save(self, user_obj):
        """ Check if the give user has permission to save (or create) this
        node.

        A user can create a new node if it:

            - Is a superuser.
            - Is admin on any parentnode.

        A user can save if it:

            - Is a superuser.
            - Is admin on any parentnode.
            - Is admin on the node.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: bool
        """
        raise NotImplementedError()
