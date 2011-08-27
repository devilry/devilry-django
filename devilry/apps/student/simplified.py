from datetime import datetime
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Count, Max
from django.template.defaultfilters import filesizeformat

from ...simplified import simplified_modelapi, SimplifiedModelApi, PermissionDenied
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,
                                                   SimplifiedFileMetaMetaMixin)
from devilry.apps.core.models import AssignmentGroup, Delivery
from devilry.utils.devilry_email import send_email



class PublishedWhereIsCandidateMixin(SimplifiedModelApi):
    """ Mixin class extended by all classes in the Simplified API for Student using the Simplified API """

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is a student.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an student in the given
        ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not cls._meta.model.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.FileMeta`. """
    class Meta(SimplifiedFileMetaMetaMixin):
        """ Defines what methods a Student can use on a FileMeta object using the Simplified API """
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        """ Defines what methods a Student can use on a Deadline object using the Simplified API """
        methods = ['search', 'read']
        editablefields = tuple()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user).annotate(number_of_deliveries=Count('deliveries'))


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.StaticFeedback`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        """ Defines what methods a Student can use on a StaticFeedback object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        """ Defines what methods a Student can use on a Delivery object using the Simplified API """
        methods = ['search', 'read', 'create', 'update']
        editablefields = ('successful', 'deadline')

    @classmethod
    def pre_full_clean(cls, user, obj):
        obj.time_of_delivery = datetime.now()
        candidate = obj.deadline.assignment_group.candidates.get(student=user)
        obj.delivered_by = candidate
        obj._set_number()

    @classmethod
    def write_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an student in the given
        ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not AssignmentGroup.published_where_is_candidate(user).filter(id=obj.deadline.assignment_group.id):
            raise PermissionDenied()
        if obj.id != None:
            current = Delivery.objects.get(id=obj.id)
            if current.successful:
                raise PermissionDenied()

    @classmethod
    def post_save(cls, user, delivery):
        if delivery.successful:
            deadline = delivery.deadline
            assignment_group = deadline.assignment_group
            assignment = assignment_group.parentnode
            period = assignment.parentnode
            subject = period.parentnode
            user_list = [candidate.student \
                    for candidate in assignment_group.candidates.all()]
            urlpath = reverse('student-show-assignmentgroup', kwargs=dict(assignmentgroupid=assignment_group.id))
            url = '{domain}{prefix}{path}?deliveryid={deliveryid}'.format(domain = settings.DEVILRY_SCHEME_AND_DOMAIN,
                                                                          prefix = settings.DEVILRY_MAIN_PAGE,
                                                                          path = urlpath,
                                                                          deliveryid = delivery.id)

            files = ''
            for fm in delivery.filemetas.all():
                files += ' - {0} ({1})\n'.format(fm.filename, filesizeformat(fm.size))

            email_subject = 'Receipt for delivery on {0}'.format(assignment.get_path())
            email_message = ('This is a receipt for your delivery.\n\n'
                             'Subject: {subject}\n'
                             'Period: {period}\n'
                             'Assignment: {assignment}\n'
                             'Deadline: {deadline}\n'
                             'Delivery number: {deliverynumer}\n'
                             'Time of delivery: {time_of_delivery}\n'
                             'Files:\n{files}\n\n'
                             'The delivery can be viewed at:\n'
                             '{url}'.format(subject = subject.long_name,
                                            period = period.long_name,
                                            assignment = assignment.long_name,
                                            deadline = deadline.deadline.isoformat(),
                                            deliverynumer = delivery.number,
                                            time_of_delivery = delivery.time_of_delivery.isoformat(),
                                            files = files,
                                            url = url))

            send_email(user_list, email_subject, email_message)



@simplified_modelapi
class SimplifiedAssignmentGroup(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.AssignmentGroup`. """
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        """ Defines what methods a Student can use on an AssignmentGroup object using the Simplified API """
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all AssignmentGroup-objects where given ``user`` is candidate.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.published_where_is_candidate(user).annotate(latest_delivery_id=Max('deadlines__deliveries__id'),
                                                                           number_of_deliveries=Count('deadlines__deliveries'))



@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(SimplifiedAssignmentMetaMixin):
        """ Defines what methods a Student can use on an Assignment object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(SimplifiedPeriodMetaMixin):
        """ Defines what methods a Student can use on a Period object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(SimplifiedSubjectMetaMixin):
        """ Defines what methods a Student can use on a Subject object using the Simplified API """
        methods = ['search', 'read']
