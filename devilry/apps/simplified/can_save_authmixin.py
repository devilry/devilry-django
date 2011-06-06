from exceptions import PermissionDenied


class CanSaveAuthMixin(object):
    @classmethod
    def authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()
