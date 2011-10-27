from django.contrib.auth.models import User
from django.db.models import Count, Max

from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied, InvalidUsername, FieldSpec,
                                FilterSpecs, FilterSpec, PatternFilterSpec,
                                stringOrNoneConverter, boolConverter)
from ..core import models
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

__all__ = ('SimplifiedNode', 'SimplifiedSubject', 'SimplifiedPeriod', 'SimplifiedAssignment', 'SimplifiedAssignmentGroup',
           'SimplifiedRelatedExaminer', 'SimplifiedRelatedStudent', 'SimplifiedRelatedStudentKeyValue', 'SimplifiedCandidate')


def _convert_list_of_usernames_to_userobjects(usernames):
    """
    Parse list of usernames to list of User objects. Each username must be an existing user.

    If all usernames are valid, usernames are returned.
    """
    users = []
    for username in usernames:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise InvalidUsername(username)
        users.append(user)
    return users


class HasAdminsMixin(object):
    class MetaMixin:
        fake_editablefields = ('fake_admins',)

    @classmethod
    def _parse_admins_as_list_of_usernames(cls, obj):
        """
        Parse admins as a a list of usernames. Each username must be an existing user.

        If all usernames are valid, ``obj.admins`` is cleared, and the
        given admins are added (I.E.: All current admins are replaced).
        """
        if hasattr(obj, 'fake_admins') and obj.fake_admins != None:
            users = _convert_list_of_usernames_to_userobjects(obj.fake_admins)
            obj.admins.clear()
            for user in users:
                obj.admins.add(user)

    @classmethod
    def post_save(cls, user, obj):
        cls._parse_admins_as_list_of_usernames(obj)



class CanSaveBase(SimplifiedModelApi):
    """ Mixin class extended by many of the classes in the Simplified API for Administrator """
    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def read_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to ``obj``, and raise
        ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is admin or superadmin.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

@simplified_modelapi
class SimplifiedNode(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Node`. """
    class Meta(HasAdminsMixin.MetaMixin):
        """ Defines the CRUD+S methods, the django model to be used, resultfields returned by
        search and which fields can be used to search for a Node object
        using the Simplified API """

        fake_editablefields = ('fake_admins',)
        methods = ['create', 'read', 'update', 'delete', 'search']

        model = models.Node
        resultfields = FieldSpec('id',
                                 'parentnode',
                                 'short_name',
                                 'long_name',
                                 admins=['admins__username'])
        searchfields = FieldSpec('short_name',
                                 'long_name')
        filters = FilterSpecs(FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              PatternFilterSpec('^(parentnode__)+short_name$'),
                              PatternFilterSpec('^(parentnode__)+long_name$'),
                              PatternFilterSpec('^(parentnode__)+id$'))


    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all node-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return models.Node.where_is_admin_or_superadmin(user)

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given node contains no childnodes or subjects.
        """
        return obj.subjects.all().count() == 0 and obj.child_nodes.all().count() == 0


@simplified_modelapi
class SimplifiedSubject(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedSubjectMetaMixin):
        """ Defines what methods an Administrator can use on a Subject object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec(admins=['admins__username']) + SimplifiedSubjectMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given subject contains no periods
        """
        return obj.periods.all().count() == 0


@simplified_modelapi
class SimplifiedPeriod(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedPeriodMetaMixin):
        """ Defines what methods an Administrator can use on a Period object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec(admins=['admins__username']) + SimplifiedPeriodMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given period contains no assignments
        """
        return obj.assignments.all().count() == 0



class RelatedUsersBase(SimplifiedModelApi):
    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all related users of this type where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user, 'period', 'user', 'user__devilryuserprofile')

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

@simplified_modelapi
class SimplifiedRelatedExaminer(RelatedUsersBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedExaminer`. """
    class Meta(RelatedUsersMetaBase):
        """ Defines what methods an Administrator can use on a RelatedExaminer object using the Simplified API """
        model = models.RelatedExaminer

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


@simplified_modelapi
class SimplifiedRelatedStudentKeyValue(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedStudentKeyValue`. """
    class Meta:
        model = models.RelatedStudentKeyValue
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec('id', 'application', 'key', 'value', 'relatedstudent', 'student_can_read')
        searchfields = FieldSpec('application', 'key', 'value', 'relatedstudent__user__username')
        editablefields = ('application', 'key', 'value', 'relatedstudent', 'student_can_read')
        filters = FilterSpecs(FilterSpec('id', supported_comp=('exact',)),
                              FilterSpec('student_can_read', supported_comp=('exact',), type_converter=boolConverter),
                              FilterSpec('application', supported_comp=('exact',)),
                              FilterSpec('relatedstudent__period', supported_comp=('exact',)),
                              FilterSpec('relatedstudent__user', supported_comp=('exact',)))

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


@simplified_modelapi
class SimplifiedAssignment(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedAssignmentMetaMixin):
        """ Defines what methods an Administrator can use on an Assignment object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec(admins=['admins__username']) + SimplifiedAssignmentMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given assignment contains no assignmentgroups.
        """
        return obj.assignmentgroups.all().count() == 0


@simplified_modelapi
class SimplifiedCandidate(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedCandidateMetaMixin):
        """ Defines what methods an Administrator can use on an Assignment object using the Simplified API """
        methods = ('create', 'read', 'update', 'delete', 'search')
        editablefields = ('student', 'candidate_id', 'assignment_group')
        resultfields = FieldSpec('student', 'candidate_id') + SimplifiedCandidateMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given assignment contains no assignmentgroups.
        """
        return models.Delivery.objects.filter(deadline__assignment_group=obj.assignment_group, delivered_by=obj).count() == 0


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


@simplified_modelapi
class SimplifiedDelivery(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        """ Defines what methods an Administrator can use on a Delivery object using the Simplified API """
        methods = ['search', 'read', 'create', 'update', 'delete']
        editablefields = ('successful', 'deadline', 'delivery_type', 'alias_delivery')

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is admin or superadmin.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def pre_full_clean(cls, user, obj):
        ExaminerSimplifiedDelivery.examiner_pre_full_clean(user, obj)

    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.deadline.assignment_group.can_save(user):
            raise PermissionDenied()
        ExaminerSimplifiedDelivery.write_authorize_examinercommon(user, obj)

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.deadline.assignment_group.can_save(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedStaticFeedback(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        """ Defines what methods an Administrator can use on a StaticFeedback object using the Simplified API """
        methods = ['search', 'read', 'delete']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all StaticFeedback-objects where given ``user`` is admin or superadmin.

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
        if not obj.delivery.deadline.assignment_group.can_save(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        """ Defines what methods an Administrator can use on a Deadline object using the Simplified API """
        methods = ['search', 'read', 'create', 'delete']
        editablefields = ('text', 'deadline', 'assignment_group',
                          'feedbacks_published')

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all Deadline-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user).annotate(number_of_deliveries=Count('deliveries'))

    @classmethod
    def read_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` is an administrator for the given
        Deadline ``obj`` or a superadmin, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline object.
        :throws PermissionDenied:
        """
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.assignment_group.is_admin(user_obj):
                raise PermissionDenied()

    @classmethod
    def write_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` can save changes to the
        AssignmentGroup of the given Deadline ``obj``, and raises
        ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline object.
        :throws PermissionDenied:
        """
        if not obj.assignment_group.can_save(user_obj):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.FileMeta`. """
    class Meta(SimplifiedFileMetaMetaMixin):
        """ Defines what methods an Administrator can use on a FileMeta object using the Simplified API """
        methods = ['search', 'read', 'delete']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all FileMeta-objects where given ``user`` is admin or superadmin.

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
        if not obj.delivery.deadline.assignment_group.can_save(user):
            raise PermissionDenied()
