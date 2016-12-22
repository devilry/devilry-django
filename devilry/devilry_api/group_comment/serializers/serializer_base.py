from django.utils.translation import ugettext_lazy
from rest_framework import serializers

from devilry.apps.core.models import Candidate, Examiner
from devilry.devilry_group.models import GroupComment


class GroupCommentSerializerBase(serializers.ModelSerializer):
    #: Group Comment published on datetime
    published_datetime = serializers.SerializerMethodField()

    #: Full name of user who posted GroupComment
    user_fullname = serializers.SerializerMethodField()

    #: Short name of user who posted GroupComment
    user_shortname = serializers.SerializerMethodField()

    class Meta:
        model = GroupComment
        fields = [
            'id',
            'feedback_set',
            'published_datetime',
            'text',
            'visibility',
            'part_of_grading',
            'user_fullname',
            'user_shortname',
            'user_role',
            'created_datetime'
        ]

    @property
    def devilry_role(self):
        """
        Override this to return 'student'
                                'examiner',
                                'periodadmin',
                                'subjectadmin' or
                                'departmentadmin'.

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def __get_candidate(self, instance):
        """
        Get Candidate object of the user who posted the comment
        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :obj:`~devilry.apps.core.Candidate`
        """
        return Candidate.objects.get(assignment_group=instance.feedback_set.group,
                                     relatedstudent__user=instance.user)

    def __get_examiner(self, instance):
        """
        Get Examiner object of the user who posted the comment
        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :obj:`~devilry.apps.core.Examiner`
        """
        return Examiner.objects.get(assignmentgroup=instance.feedback_set.group,
                                    relatedexaminer__user=instance.user)

    def __student_fullname_anonymization(self, instance):
        """
        Returns student's full name or anonymized name of the user who posted the comment.

        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :attr:`~devilry_account.User.fullname` or anonymized name of student user.

        """
        anonymous = instance.feedback_set.group.parentnode \
            .students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return self.__get_candidate(instance).get_anonymous_name()
        return instance.user.fullname

    def __student_shortname_anonymization(self, instance):
        """
        Returns student's short name or anonymized name of the user who posted the comment.

        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :attr:`~devilry_account.shortname` or anonymized name of student user.

        """
        anonymous = instance.feedback_set.group.parentnode \
            .students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return self.__get_candidate(instance).get_anonymous_name()
        return instance.user.shortname

    def __examiner_fullname_anonymization(self, instance):
        """
        Returns examiner's full name or anonymized name of the user who posted the comment.

        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :attr:`~devilry_account.fullname` or anonymized name of examiner user.

        """
        anonymous = instance.feedback_set.group.parentnode \
            .examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return self.__get_examiner(instance).get_anonymous_name()
        return instance.user.fullname

    def __examiner_shortname_anonymization(self, instance):
        """
        Returns examiner's short name or anonymized name of the user who posted the comment.

        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :attr:`~devilry_account.shortname` or anonymized name of examiner user.

        """
        anonymous = instance.feedback_set.group.parentnode \
            .examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return self.__get_examiner(instance).get_anonymous_name()
        return instance.user.shortname

    def get_published_datetime(self, instance):
        """
        Gets published datetime of comment.
        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :method:`~devilry_group.GroupComment.get_published_datetime`

        """
        return instance.get_published_datetime()

    def get_user_fullname(self, instance):
        """
        Gets full name or anonymized name of user who posted the comment.

        TODO: admin stuff
        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :attr:`~devilry_account.User.fullname` or anonimized name of user.

        """
        if instance.user_role == GroupComment.USER_ROLE_STUDENT:
            return self.__student_fullname_anonymization(instance)
        elif instance.user_role == GroupComment.USER_ROLE_EXAMINER:
            return self.__examiner_fullname_anonymization(instance)
        elif instance.user_role == GroupComment.USER_ROLE_ADMIN:
            #TODO: admin name
            return 'Admin'
        raise serializers.ValidationError(ugettext_lazy('Not valid user role'))

    def get_user_shortname(self, instance):
        """
        Gets short name or anonymized name of user who posted the comment.

        TODO: admin stuff
        Args:
            instance: :obj:`~devilry_group.GroupComment`

        Returns:
            :attr:`~devilry_account.User.shortname` or anonimized name of user.

        """
        if instance.user_role == GroupComment.USER_ROLE_STUDENT:
            return self.__student_shortname_anonymization(instance)
        elif instance.user_role == GroupComment.USER_ROLE_EXAMINER:
            return self.__examiner_shortname_anonymization(instance)
        elif instance.user_role == GroupComment.USER_ROLE_ADMIN:
            #TODO: admin name
            return 'Admin'
        raise serializers.ValidationError(ugettext_lazy('Not valid user role'))
