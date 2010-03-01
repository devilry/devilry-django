from django import forms
from django.db import models


class PermMixin(object):
    @classmethod
    def get_changelist(cls, user_obj):
        raise NotImplementedError('get_changelist must be implemented in subclass.')

    @classmethod
    def has_obj_permission(cls, user_obj, perm, obj):
        """ Check permissions for user on the given object of this model. """
        if 'change_' in perm:
            return cls.get_changelist(user_obj).filter(pk=obj.pk).count() > 0
        elif 'delete_' in perm:
            for field in cls.iter_authmodel_fks():
                qry = field.related.parent_model.get_changelist(user_obj)
                if qry.count() == 0:
                    return False
                elif qry.count() == 1:
                    if qry.all()[0] == obj:
                        return False
            return True
        return False

    @classmethod
    def has_model_permission(cls, user_obj, perm):
        """
        Check permissions for user on this model. When object/instance
        permission is required, `has_obj_permission`_ is called instead.
        """
        if 'change_' in perm:
            return cls.get_changelist(user_obj).count() != 0
        return False

    @staticmethod
    def is_permmixin_model(modelcls):
        return hasattr(modelcls, 'get_changelist')


    @classmethod
    def iter_authmodel_fks(cls):
        for field in iter(cls._meta.fields):
            if isinstance(field, ForeignKey):
                yield field


class ForeignKey(models.ForeignKey):
    def formfield(self, user_obj=None, **kwargs):
        if user_obj == None:
            return models.query.EmptyQuerySet()
        db = kwargs.pop('using', None)
        qry = self.related.parent_model.get_changelist(user_obj)
        defaults = {
            'form_class': forms.ModelChoiceField,
            'queryset': qry,
            'to_field_name': self.rel.field_name,
        }
        defaults.update(kwargs)
        return super(models.ForeignKey, self).formfield(**defaults)
