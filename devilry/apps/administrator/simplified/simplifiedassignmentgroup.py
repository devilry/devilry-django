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

from helpers import _convert_list_of_usernames_to_userobjects
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedAssignmentGroup(CanSaveBase):
    """ Simplified wrapper for
    :class:`devilry.apps.core.models.AssignmentGroup`. """
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        """ Defines what methods an Administrator can use on an AssignmentGroup object using the Simplified API """
        editablefields = ('id', 'name', 'is_open', 'parentnode')
        fake_editablefields = ('fake_examiners', 'fake_candidates', 'fake_tags')
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = \
                FieldSpec(users=['candidates__student__username'],
                          tags=['tags__tag']) + \
                SimplifiedAssignmentGroupMetaMixin.resultfields
        searchfields = FieldSpec('tags__tag', 'candidates__student__username') + SimplifiedAssignmentGroupMetaMixin.searchfields
        filters = SimplifiedAssignmentGroupMetaMixin.filters + \
                FilterSpecs(FilterSpec('candidates__student__username', type_converter=stringOrNoneConverter),
                            FilterSpec('examiners__username', type_converter=stringOrNoneConverter),
                            FilterSpec('tags__tag', type_converter=stringOrNoneConverter))


    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all Deadline-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user, 'feedback', 'parentnode').annotate(latest_delivery_id=Max('deadlines__deliveries__id'),
                                                                                                     latest_deadline_id=Max('deadlines__id'),
                                                                                                     latest_deadline_deadline=Max('deadlines__deadline'),
                                                                                                     number_of_deliveries=Count('deadlines__deliveries'))

    @classmethod
    def _parse_examiners_as_list_of_usernames(cls, obj):
        """
        Parse examiners as a a list of usernames. Each username must be an existing user.

        If all usernames are valid, ``obj.examiners`` is cleared, and the
        given examiners are added (I.E.: All current examiners are replaced).
        """
        if hasattr(obj, 'fake_examiners') and obj.fake_examiners != None:
            users = _convert_list_of_usernames_to_userobjects(obj.fake_examiners)
            obj.examiners.clear()
            for user in users:
                obj.examiners.add(user)

    @classmethod
    def _set_tags_from_fake_tags(cls, obj):
        """  """
        if hasattr(obj, 'fake_tags') and obj.fake_tags != None:
            models.AssignmentGroupTag.objects.filter(assignment_group=obj).delete()
            for tag in obj.fake_tags:
                obj.tags.create(tag=tag)

    @classmethod
    def _parse_candidates_as_list_of_dicts(cls, obj):
        """
        Parse candidates as a a list of dicts. Each dict should have the
        following key,value pairs:

            username
                The username of an existing user. This key,value pair is required.
                The user with the given username is created as a candidate.
            candidate_id
                The candidate_id. This is optional, and defaults to ``None``.

        If all usernames are valid, ``obj.candidates`` is cleared, and the
        given candidates are added (I.E.: All current candidates are replaced).
        """
        if hasattr(obj, 'fake_candidates') and obj.fake_candidates != None:
            new_candidates_usernames = [candidatespec['username'] for candidatespec in obj.fake_candidates]
            to_delete = []
            for candidate in obj.candidates.all():
                if not candidate.student.username in new_candidates_usernames:
                    if models.Delivery.objects.filter(deadline__assignment_group=obj, delivered_by=candidate).count() != 0:
                        raise PermissionDenied('You can not remove {0} from the group. Candidates that have made a delivery can not be removed.'.format(candidate.student.username))
                    to_delete.append(candidate)
            for candidate in to_delete:
                candidate.delete()

            create_kwargs = []
            update_candidates = []
            for candidatespec in obj.fake_candidates:
                username = candidatespec['username']
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise InvalidUsername(username)
                else:
                    candidate_id = candidatespec.get('candidate_id', None)
                    try:
                        candiate = obj.candidates.get(student__username=username)
                    except models.Candidate.DoesNotExist:
                        candidatekwargs = dict(student = user,
                                               candidate_id = candidate_id)
                        create_kwargs.append(candidatekwargs)
                    else:
                        update_candidates.append((candiate, candidate_id))
            for candidate, candidate_id in update_candidates:
                candidate.candidate_id = candidate_id
                candidate.save()
            for candidatekwargs in create_kwargs:
                obj.candidates.create(**candidatekwargs)

    @classmethod
    def post_save(cls, user, obj):
        cls._parse_examiners_as_list_of_usernames(obj)
        cls._parse_candidates_as_list_of_dicts(obj)
        cls._set_tags_from_fake_tags(obj)

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given assignmentgroup contains no deliveries.
        """
        return models.Delivery.objects.filter(deadline__assignment_group=obj).count() == 0
