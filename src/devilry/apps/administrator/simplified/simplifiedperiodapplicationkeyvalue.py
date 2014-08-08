from devilry.simplified import (simplified_modelapi,
                                PermissionDenied, FieldSpec,
                                FilterSpecs, FilterSpec)
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import SimplifiedAbstractApplicationKeyValueMixin

from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedPeriodApplicationKeyValue(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedStudentKeyValue`. """
    class Meta(SimplifiedAbstractApplicationKeyValueMixin):
        model = models.PeriodApplicationKeyValue
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec('period') + SimplifiedAbstractApplicationKeyValueMixin.resultfields
        editablefields = ('period',) + SimplifiedAbstractApplicationKeyValueMixin.editablefields
        filters = FilterSpecs(FilterSpec('period', supported_comp=('exact',)),
                              FilterSpec('period__start_time'),
                              FilterSpec('period__end_time'),
                              FilterSpec('period__parentnode', supported_comp=('exact',)),
                              FilterSpec('period__parentnode__parentnode', supported_comp=('exact',))
                             ) + SimplifiedAbstractApplicationKeyValueMixin.filters

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all related users of this type where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.period.can_save(user):
            raise PermissionDenied()

    @classmethod
    def is_empty(cls, obj):
        return True
