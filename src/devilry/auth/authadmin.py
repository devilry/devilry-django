from django.contrib import admin
import authmodel


class ModelAdminMixin(object):
    """ Mixin for `django.contrib.admin.ModelAdmin` where the obj-argument in
    has_change_permission and has_delete_permission is forwarded to the
    auth backend. Must be mixed in *before* ModelAdmin. Example::
        >>> class ExampleModelAdmin(InstanceAuthModelAdmin, admin.ModelAdmin):
        ...    list_display = ['test', 'field']
    """

    def queryset(self, request):
        return self.model.get_changelist(request.user)

    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to change *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(
                opts.app_label + '.' + opts.get_change_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(
                opts.app_label + '.' + opts.get_delete_permission(), obj)

    def has_student_permission(self, request, obj=None):
        return False
    def has_examiner_permission(self, request, obj=None):
        return False


    def get_model_perms(self, request):
        """
        Returns a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'student': self.has_student_permission(request),
            'examiner': self.has_examiner_permission(request),
        }

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if isinstance(db_field, authmodel.ForeignKey):
            return db_field.formfield(request.user, **kwargs)
        return db_field.formfield(**kwargs)


    def get_readonly_fields(self, request, obj=None):
        if obj:
            r = []
            for field in obj.iter_authmodel_fks():
                parent_model = field.related.parent_model
                if parent_model.get_changelist(request.user).count() == 0:
                    r.append(field.name)
            r.extend(self.readonly_fields)
            return r
        return self.readonly_fields



class ModelAdmin(ModelAdminMixin, admin.ModelAdmin):
    """ ModelAdmin with `PermMixinModelAdminMixin`. """
