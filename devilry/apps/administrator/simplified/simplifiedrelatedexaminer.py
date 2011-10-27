from devilry.simplified import simplified_modelapi
from devilry.apps.core import models

from relatedusersbase import RelatedUsersBase
from relatedusersmetabase import RelatedUsersMetaBase


@simplified_modelapi
class SimplifiedRelatedExaminer(RelatedUsersBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedExaminer`. """
    class Meta(RelatedUsersMetaBase):
        """ Defines what methods an Administrator can use on a RelatedExaminer object using the Simplified API """
        model = models.RelatedExaminer
