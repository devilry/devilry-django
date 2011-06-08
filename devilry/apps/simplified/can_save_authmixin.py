from exceptions import PermissionDenied


class CanSaveAuthMixin(object):
    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()
