from devilry.simplified import (simplified_modelapi, FieldSpec, FilterSpecs,
                                FilterSpec)
from devilry.apps.core import models

from relatedusersbase import RelatedUsersBase
from relatedusersmetabase import RelatedUsersMetaBase


@simplified_modelapi
class SimplifiedRelatedStudent(RelatedUsersBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedStudent`. """
    class Meta(RelatedUsersMetaBase):
        """ Defines what methods an Administrator can use on a RelatedStudent object using the Simplified API """
        model = models.RelatedStudent
        resultfields = RelatedUsersMetaBase.resultfields + FieldSpec('candidate_id')
        searchfields = RelatedUsersMetaBase.searchfields + FieldSpec('candidate_id')
        editablefields = RelatedUsersMetaBase.editablefields + ('candidate_id',)
        filters = RelatedUsersMetaBase.filters + FilterSpecs(FilterSpec('candidate_id'))
