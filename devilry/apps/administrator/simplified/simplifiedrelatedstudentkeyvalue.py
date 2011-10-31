from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied, FieldSpec,
                                FilterSpecs, FilterSpec,
                                boolConverter)
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import SimplifiedAbstractApplicationKeyValueMixin


@simplified_modelapi
class SimplifiedRelatedStudentKeyValue(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedStudentKeyValue`. """
    class Meta(SimplifiedAbstractApplicationKeyValueMixin):
        model = models.RelatedStudentKeyValue
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec('relatedstudent', 'student_can_read') + SimplifiedAbstractApplicationKeyValueMixin.resultfields
        searchfields = FieldSpec('relatedstudent__user__username') + SimplifiedAbstractApplicationKeyValueMixin.searchfields
        editablefields = ('relatedstudent', 'student_can_read') + SimplifiedAbstractApplicationKeyValueMixin.editablefields
        filters = FilterSpecs(FilterSpec('student_can_read', supported_comp=('exact',), type_converter=boolConverter),
                              FilterSpec('relatedstudent__period', supported_comp=('exact',)),
                              FilterSpec('relatedstudent__user', supported_comp=('exact',))) + SimplifiedAbstractApplicationKeyValueMixin.filters

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
        if not obj.relatedstudent.period.can_save(user):
            raise PermissionDenied()

    @classmethod
    def is_empty(cls, obj):
        return True
