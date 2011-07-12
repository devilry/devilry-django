from ...simplified import simplified_modelapi, SimplifiedModelApi, PermissionDenied
from simplifiedmetabases import (SimplifiedSubjectMetaMixin, SimplifiedPeriodMetaMixin,
                                 SimplifiedAssignmentMetaMixin, SimplifiedAssignmentGroupMetaMixin,
                                 SimplifiedDeadlineMetaMixin, SimplifiedDeliveryMetaMixin,
                                 SimplifiedStaticFeedbackMetaMixin, SimplifiedFileMetaMetaMixin)


class PublishedWhereIsCandidateMixin(SimplifiedModelApi):

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedFileMetaMetaMixin):
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsCandidateMixin):
    class Meta(SimplifiedDeadlineMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedDeliveryMetaMixin):
        methods = ['search', 'read', 'delete']


@simplified_modelapi
class SimplifiedAssignmentGroup(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedAssignmentMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedPeriodMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedSubjectMetaMixin):
        methods = ['search', 'read']
