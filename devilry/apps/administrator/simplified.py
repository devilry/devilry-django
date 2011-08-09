from django.contrib.auth.models import User
from django.db.models import Count

from ...simplified import (SimplifiedModelApi, simplified_modelapi,
                           PermissionDenied, FieldSpec,
                           FilterSpecs, FilterSpec, PatternFilterSpec)
from ..core import models
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,
                                                   SimplifiedFileMetaMetaMixin)

__all__ = ('SimplifiedNode', 'SimplifiedSubject', 'SimplifiedPeriod', 'SimplifiedAssignment')



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
class SimplifiedNode(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Node`. """
    class Meta:
        """ Defines the CRUD+S methods, the django model to be used, resultfields returned by
        search and which fields can be used to search for a Node object
        using the Simplified API """

        methods = ['create', 'read', 'update', 'delete', 'search']

        model = models.Node
        resultfields = FieldSpec('id',
                                 'parentnode',
                                 'short_name',
                                 'long_name')
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
class SimplifiedSubject(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(SimplifiedSubjectMetaMixin):
        """ Defines what methods an Administrator can use on a Subject object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given subject contains no periods
        """
        return obj.periods.all().count() == 0


@simplified_modelapi
class SimplifiedPeriod(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(SimplifiedPeriodMetaMixin):
        """ Defines what methods an Administrator can use on a Period object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']

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

class RelatedUsersMetaBase:
    methods = ['create', 'read', 'update', 'delete', 'search']
    resultfields = FieldSpec('id', 'username', 'period')
    searchfields = FieldSpec('username')
    editablefields = ('username', 'period')
    filters = FilterSpecs(FilterSpec('period'),
                          FilterSpec('username'))

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


@simplified_modelapi
class SimplifiedAssignment(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(SimplifiedAssignmentMetaMixin):
        """ Defines what methods an Administrator can use on an Assignment object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given assignment contains no assignmentgroups.
        """
        return obj.assignmentgroups.all().count() == 0

@simplified_modelapi
class SimplifiedAssignmentGroup(CanSaveBase):
    """ Simplified wrapper for
    :class:`devilry.apps.core.models.AssignmentGroup`. """
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        """ Defines what methods an Administrator can use on an AssignmentGroup object using the Simplified API """
        editablefields = ('id', 'name', 'is_open', 'parentnode')
        fake_editablefields = ('fake_examiners', 'fake_candidates')
        methods = ['create', 'read', 'update', 'delete', 'search']


    @classmethod
    def _parse_examiners_as_list_of_usernames(cls, obj):
        """
        Parse examiners as a a list of usernames. Each username must be an existing user.

        If all usernames are valid, ``obj.examiners`` is cleared, and the
        given examiners are added (I.E.: All current examiners are replaced).
        """
        if hasattr(obj, 'fake_examiners'):
            fake_examiners = obj.fake_examiners
            users = []
            for username in fake_examiners:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise PermissionDenied()
                users.append(user)
            obj.examiners.clear()
            for user in users:
                obj.examiners.add(user)

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
        if hasattr(obj, 'fake_candidates'):
            candidateskwargs = []
            for candidatespec in obj.fake_candidates:
                try:
                    user = User.objects.get(username=candidatespec['username'])
                except User.DoesNotExist:
                    raise PermissionDenied()
                else:
                    candidatekwargs = dict(student = user,
                                           candidate_id = candidatespec.get('candidate_id', None))
                    candidateskwargs.append(candidatekwargs)
            models.Candidate.objects.filter(assignment_group=obj).delete() # Clear current candidates
            for candidatekwargs in candidateskwargs:
                obj.candidates.create(**candidatekwargs)

    @classmethod
    def post_save(cls, user, obj):
        cls._parse_examiners_as_list_of_usernames(obj)
        cls._parse_candidates_as_list_of_dicts(obj)


@simplified_modelapi
class SimplifiedDelivery(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        """ Defines what methods an Administrator can use on a Delivery object using the Simplified API """
        methods = ['search', 'read'] #, 'create', 'update', 'delete'] # TODO: Delivered by administrator?

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
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
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
