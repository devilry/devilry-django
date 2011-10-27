from django.contrib.auth.models import User
from django.db.models import Count, Max

from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied, InvalidUsername, FieldSpec,
                                FilterSpecs, FilterSpec, PatternFilterSpec,
                                stringOrNoneConverter, boolConverter)
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,
                                                   SimplifiedFileMetaMetaMixin,
                                                   SimplifiedCandidateMetaMixin)
from devilry.apps.examiner.simplified import SimplifiedDelivery as ExaminerSimplifiedDelivery


class RelatedUsersMetaBase:
    methods = ['create', 'read', 'update', 'delete', 'search']
    resultfields = FieldSpec('id', 'period', 'user', 'tags',
                             'user__username',
                             'user__devilryuserprofile__full_name',
                             'user__email')
    searchfields = FieldSpec('user__username', 'user__devilryuserprofile__full_name')
    editablefields = ('period', 'user')
    filters = FilterSpecs(FilterSpec('id', supported_comp=('exact',)),
                          FilterSpec('period', supported_comp=('exact',)),
                          FilterSpec('user', supported_comp=('exact',)))
