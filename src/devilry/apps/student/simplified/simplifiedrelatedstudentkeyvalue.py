from devilry.simplified import (simplified_modelapi, SimplifiedModelApi,
                                PermissionDenied, FieldSpec,
                                FilterSpecs, FilterSpec)
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import SimplifiedAbstractApplicationKeyValueMixin


@simplified_modelapi
class SimplifiedRelatedStudentKeyValue(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedStudentKeyValue`. """
    class Meta:
        model = models.RelatedStudentKeyValue
        methods = ['read', 'search']
        resultfields = FieldSpec('relatedstudent', 'relatedstudent__period') + SimplifiedAbstractApplicationKeyValueMixin.resultfields
        searchfields = SimplifiedAbstractApplicationKeyValueMixin.searchfields
        filters = FilterSpecs(FilterSpec('relatedstudent__period', supported_comp=('exact',))) + SimplifiedAbstractApplicationKeyValueMixin.filters

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.objects.filter(relatedstudent__user=user, student_can_read=True)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls.create_searchqryset(user).filter(id=obj.id):
            raise PermissionDenied()
