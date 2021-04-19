from datetime import timedelta

import arrow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core.deliverystore import MemoryDeliveryStore
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Deadline
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import FileMeta
from devilry.apps.core.models import Period
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.models import StaticFeedbackFileAttachment
from devilry.apps.core.models import Subject
from devilry.devilry_comment.models import CommentFile


class ReloadableDbBuilderInterface(object):
    def update(self, **attributes):
        raise NotImplementedError()

    def reload_from_db(self):
        raise NotImplementedError()


class UserBuilder(ReloadableDbBuilderInterface):
    """
    The old user builder class.

    Use :class:`.UserBuilder2` for new tests.
    """

    def __init__(self, username, full_name=None, email=None, is_superuser=False):
        email = email or '{}@example.com'.format(username)
        if settings.CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND:
            username = ''
        self.user = get_user_model().objects.create_user(
            username=username,
            email=email,
            is_superuser=is_superuser,
            password='test',
            fullname=full_name or '')

    def update(self, **attributes):
        for attrname, value in attributes.items():
            setattr(self.user, attrname, value)
        self.user.save()
        self.reload_from_db()

    def reload_from_db(self):
        self.user = get_user_model().objects.get(id=self.user.id)


class UserBuilder2(ReloadableDbBuilderInterface):
    """
    A user builder much more suitable for :class:`devilry.devilry_account.model.User`
    than :class:`.UserBuilder`.

    Use this insted of :class:`.UserBuilder` for new tests.
    """

    def __init__(self, **kwargs):
        self.user = baker.make_recipe('devilry.devilry_account.user', **kwargs)
        self.user.save()

    def update(self, **attributes):
        for attrname, value in attributes.items():
            setattr(self.user, attrname, value)
        self.user.save()
        self.reload_from_db()

    def reload_from_db(self):
        self.user = get_user_model().objects.get(id=self.user.id)

    def add_emails(self, *emails):
        for email in emails:
            self.user.useremail_set.create(email=email, use_for_notifications=False)
        return self

    def add_primary_email(self, email, use_for_notifications=True):
        self.user.useremail_set.create(email=email, use_for_notifications=use_for_notifications,
                                       is_primary=True)
        return self

    def add_usernames(self, *usernames):
        for username in usernames:
            self.user.username_set.create(username=username, is_primary=False)
        return self

    def add_notification_emails(self, *emails):
        for email in emails:
            self.user.useremail_set.create(email=email, use_for_notifications=True)
        return self

    def add_primary_username(self, username):
        self.user.username_set.create(username=username, is_primary=True)
        return self


class CoreBuilderBase(ReloadableDbBuilderInterface):
    object_attribute_name = None

    def _save(self):
        getattr(self, self.object_attribute_name).save()

    def get_object(self):
        return getattr(self, self.object_attribute_name)

    def __set_object_value(self, attribute, value):
        setattr(self.get_object(), attribute, value)

    def update(self, **attributes):
        for attribute, value in attributes.items():
            self.__set_object_value(attribute, value)
        self._save()
        self.reload_from_db()

    def reload_from_db(self):
        obj = getattr(self, self.object_attribute_name)
        setattr(self, self.object_attribute_name, obj.__class__.objects.get(pk=obj.pk))

    @classmethod
    def make(cls, **kwargs):
        """
        Creates a usable object of this builders model.

        Use this when you just need an object with no special
        meaning.
        """
        raise NotImplementedError()


class BaseNodeBuilderBase(CoreBuilderBase):
    modelcls = None

    #: Used to generate unique names.
    sequencenumber = 0

    def __init__(self, short_name=None, long_name=None, **kwargs):
        if not short_name:
            short_name = '{}{}'.format(self.object_attribute_name,
                                       self.sequencenumber)
        full_kwargs = {
            'short_name': short_name,
            'long_name': long_name or short_name
        }
        full_kwargs.update(kwargs)
        setattr(self, self.object_attribute_name, self.modelcls.objects.create(**full_kwargs))
        BaseNodeBuilderBase.sequencenumber += 1

    def add_admins(self, *users):
        for user in users:
            obj = getattr(self, self.object_attribute_name)
            obj.admins.add(user)
        return self


class FileMetaBuilder(CoreBuilderBase):
    object_attribute_name = 'filemeta'

    def __init__(self, delivery, filename, data):
        self.filemeta = FileMeta.objects.create(delivery=delivery, filename=filename, size=0)
        f = FileMeta.deliverystore.write_open(self.filemeta)
        f.write(data)
        f.close()
        self.filemeta.size = len(data)
        self.filemeta.save()


class StaticFeedbackFileAttachmentBuilder(CoreBuilderBase):
    object_attribute_name = 'fileattachment'

    def __init__(self, staticfeedback, filename='test.txt', filedata='Testdata'):
        self.fileattachment = StaticFeedbackFileAttachment(staticfeedback=staticfeedback, filename=filename)
        self.fileattachment.file.save(filename, ContentFile(filedata))


class StaticFeedbackBuilder(CoreBuilderBase):
    object_attribute_name = 'feedback'

    def __init__(self, **kwargs):
        self.feedback = StaticFeedback.objects.create(**kwargs)

    def add_fileattachment(self, **kwargs):
        kwargs['staticfeedback'] = self.feedback
        return StaticFeedbackFileAttachmentBuilder(**kwargs)


class DeliveryBuilder(CoreBuilderBase):
    object_attribute_name = 'delivery'

    @classmethod
    def set_memory_deliverystore(cls):
        FileMeta.deliverystore = MemoryDeliveryStore()

    def __init__(self, **kwargs):
        if 'time_of_delivery' not in kwargs:
            kwargs['time_of_delivery'] = timezone.now()
        self.delivery = Delivery(**kwargs)
        if 'number' not in kwargs:
            self.delivery.set_number()
        self.delivery.save()

    def _save(self):
        self.delivery.save()

    def add_filemeta(self, **kwargs):
        kwargs['delivery'] = self.delivery
        return FileMetaBuilder(**kwargs)

    def add_feedback(self, **kwargs):
        kwargs['delivery'] = self.delivery
        return StaticFeedbackBuilder(**kwargs)

    def add_passed_feedback(self, **kwargs):
        kwargs['points'] = 1
        kwargs['grade'] = 'Passed'
        kwargs['is_passing_grade'] = True
        kwargs['delivery'] = self.delivery
        return StaticFeedbackBuilder(**kwargs)

    def add_failed_feedback(self, **kwargs):
        kwargs['points'] = 0
        kwargs['grade'] = 'Failed'
        kwargs['is_passing_grade'] = False
        kwargs['delivery'] = self.delivery
        return StaticFeedbackBuilder(**kwargs)

    def add_passed_A_feedback(self, **kwargs):
        kwargs['points'] = 100
        kwargs['grade'] = 'A'
        kwargs['is_passing_grade'] = True
        kwargs['delivery'] = self.delivery
        return StaticFeedbackBuilder(**kwargs)

    def add_failed_F_feedback(self, **kwargs):
        kwargs['points'] = 0
        kwargs['grade'] = 'F'
        kwargs['is_passing_grade'] = False
        kwargs['delivery'] = self.delivery
        return StaticFeedbackBuilder(**kwargs)


class DeadlineBuilder(CoreBuilderBase):
    object_attribute_name = 'deadline'

    def __init__(self, **kwargs):
        self.deadline = Deadline.objects.create(**kwargs)

    def add_delivery(self, **kwargs):
        kwargs['deadline'] = self.deadline
        kwargs['successful'] = kwargs.get('successful', True)
        return DeliveryBuilder(**kwargs)

    def add_delivery_after_deadline(self, timedeltaobject, **kwargs):
        if 'time_of_delivery' in kwargs:
            raise ValueError(
                'add_delivery_after_deadline does not accept ``time_of_delivery`` as kwarg, it sets it automatically.')
        kwargs['time_of_delivery'] = self.deadline.deadline + timedeltaobject
        return self.add_delivery(**kwargs)

    def add_delivery_before_deadline(self, timedeltaobject, **kwargs):
        if 'time_of_delivery' in kwargs:
            raise ValueError(
                'add_delivery_before_deadline does not accept ``time_of_delivery`` as kwarg, it sets it automatically.')
        kwargs['time_of_delivery'] = self.deadline.deadline - timedeltaobject
        return self.add_delivery(**kwargs)

    def add_delivery_x_hours_after_deadline(self, hours, **kwargs):
        return self.add_delivery_after_deadline(timedelta(hours=hours), **kwargs)

    def add_delivery_x_hours_before_deadline(self, hours, **kwargs):
        return self.add_delivery_before_deadline(timedelta(hours=hours), **kwargs)


class CommentFileBuilder(CoreBuilderBase):
    object_attribute_name = 'comment_file'

    def __init__(self, **kwargs):
        fileobject = ContentFile(kwargs['data'], kwargs['filename'])
        del (kwargs['data'])
        kwargs['filesize'] = fileobject.size

        self.comment_file = CommentFile.objects.create(**kwargs)
        self.comment_file.file = fileobject
        self.comment_file.save()


class GroupCommentBuilder(CoreBuilderBase):
    object_attribute_name = 'groupcomment'

    @classmethod
    def quickadd_ducku_duck1010_active_assignment1_group_feedbackset_groupcomment(cls, studentuser=None, examiner=None,
                                                                                  comment=None):
        students = []
        if studentuser:
            students.append(studentuser)
        return FeedbackSetBuilder \
            .quickadd_ducku_duck1010_active_assignment1_group_feedbackset(studentuser=studentuser, examiner=examiner) \
            .add_groupcomment(
                user=studentuser,
                user_role='student',
                instant_publish=True,
                visible_for_students=True,
                text=comment if comment is not None else 'Lorem ipsum I dont know it from memory bla bla bla..',
                published_datetime=arrow.get(timezone.now()).replace(weeks=-4, days=-3, hours=-10).datetime)

    def __init__(self, **kwargs):
        kwargs['comment_type'] = 'groupcomment'
        self.groupcomment = baker.make('devilry_group.GroupComment', **kwargs)

    def add_file(self, **kwargs):
        kwargs['comment'] = self.groupcomment
        return CommentFileBuilder(**kwargs)

    def add_files(self, files):
        retval = []
        for fileobject in files:
            retval.append(self.add_file(**fileobject))

    @classmethod
    def make(cls, **kwargs):
        feedbacksetbuilder_kwargs = {}
        for key in list(kwargs.keys()):
            if key.startswith('feedback_set__'):
                feedbacksetbuilder_kwargs[key[len('feedback_set__'):]] = kwargs.pop(key)
        groupbuilder = FeedbackSetBuilder.make(**feedbacksetbuilder_kwargs)
        return cls(feedback_set=groupbuilder.feedback_set, **kwargs)


class FeedbackSetBuilder(CoreBuilderBase):
    object_attribute_name = 'feedback_set'

    @classmethod
    def quickadd_ducku_duck1010_active_assignment1_group_feedbackset(cls, studentuser=None, examiner=None):
        students = []
        if studentuser:
            students.append(studentuser)
        return AssignmentGroupBuilder \
            .quickadd_ducku_duck1010_active_assignment1_group(studentuser=studentuser) \
            .add_feedback_set(points=10,
                              published_by=examiner,
                              created_by=examiner,
                              deadline_datetime=arrow.get(timezone.now()).replace(weeks=-4).datetime)

    def __init__(self, **kwargs):
        self.feedback_set = baker.make('devilry_group.FeedbackSet', **kwargs)

    def add_groupcomment(self, files=[], **kwargs):
        kwargs['feedback_set'] = self.feedback_set
        groupcomment = GroupCommentBuilder(**kwargs)
        groupcomment.add_files(files)
        return groupcomment.groupcomment

    @classmethod
    def make(cls, **kwargs):
        groupbuilder_kwargs = {}
        for key in list(kwargs.keys()):
            if key.startswith('group__'):
                groupbuilder_kwargs[key[len('group__'):]] = kwargs.pop(key)
        groupbuilder = AssignmentGroupBuilder.make(**groupbuilder_kwargs)
        return cls(group=groupbuilder.group, **kwargs)


class AssignmentGroupBuilder(CoreBuilderBase):
    object_attribute_name = 'group'

    @classmethod
    def quickadd_ducku_duck1010_active_assignment1_group(cls, studentuser=None):
        students = []
        if studentuser:
            students.append(studentuser)
        return AssignmentBuilder \
            .quickadd_ducku_duck1010_active_assignment1() \
            .add_group(students=students)

    def __init__(self, students=[], candidates=[], examiners=[], relatedstudents=[], **kwargs):
        self.group = AssignmentGroup.objects.create(**kwargs)
        self.add_students(*students)
        self.add_candidates(*candidates)
        self.add_examiners(*examiners)
        self.add_candidates_from_relatedstudents(*relatedstudents)

    def add_candidates_from_relatedstudents(self, *relatedstudents):
        for relatedstudent in relatedstudents:
            self.group.candidates.create(relatedstudent=relatedstudent,
                                         student_id=relatedstudent.user_id)

    def add_students(self, *users):
        for user in users:
            period = self.group.period
            relatedstudent = RelatedStudent.objects.get_or_create(user=user,
                                                                  period=period)[0]
            self.group.candidates.create(relatedstudent=relatedstudent)
        return self

    def add_candidates(self, *candidates):
        for candidate in candidates:
            self.group.candidates.add(candidate)
        return self

    def add_examiners(self, *users):
        for user in users:
            period = self.group.period
            relatedexaminer = RelatedExaminer.objects.get_or_create(user=user, period=period)[0]
            self.group.examiners.create(relatedexaminer=relatedexaminer)
        return self

    def add_deadline(self, **kwargs):
        kwargs['assignment_group'] = self.group
        return DeadlineBuilder(**kwargs)

    def add_deadline_in_x_weeks(self, weeks, **kwargs):
        if 'deadline' in kwargs:
            raise ValueError('add_deadline_in_x_weeks does not accept ``deadline`` as kwarg, it sets it automatically.')
        kwargs['deadline'] = arrow.get(timezone.now()).replace(weeks=+weeks).datetime
        return self.add_deadline(**kwargs)

    def add_deadline_x_weeks_ago(self, weeks, **kwargs):
        if 'deadline' in kwargs:
            raise ValueError(
                'add_deadline_x_weeks_ago does not accept ``deadline`` as kwarg, it sets it automatically.')
        kwargs['deadline'] = arrow.get(timezone.now()).replace(weeks=-weeks).datetime
        return self.add_deadline(**kwargs)

    def add_feedback_set(self, **kwargs):
        kwargs['group'] = self.group
        return FeedbackSetBuilder(**kwargs)

    @classmethod
    def make(cls, **kwargs):
        assignmentbuilder_kwargs = {}
        for key in list(kwargs.keys()):
            if key.startswith('assignment__'):
                assignmentbuilder_kwargs[key[len('assignment__'):]] = kwargs.pop(key)
        assignmentbuilder = AssignmentBuilder.make(**assignmentbuilder_kwargs)
        return cls(parentnode=assignmentbuilder.assignment, **kwargs)


class AssignmentBuilder(BaseNodeBuilderBase):
    object_attribute_name = 'assignment'
    modelcls = Assignment

    @classmethod
    def quickadd_ducku_duck1010_active_assignment1(cls):
        return PeriodBuilder.quickadd_ducku_duck1010_active() \
            .add_assignment('assignment1')

    def __init__(self, *args, **kwargs):
        if not 'publishing_time' in kwargs:
            kwargs['publishing_time'] = timezone.now()
        super(AssignmentBuilder, self).__init__(*args, **kwargs)

    def add_group(self, *args, **kwargs):
        kwargs['parentnode'] = self.assignment
        return AssignmentGroupBuilder(*args, **kwargs)

    @classmethod
    def make(cls, **kwargs):
        if 'publishing_time' in kwargs:
            return PeriodBuilder.make().add_assignment(**kwargs)
        else:
            return PeriodBuilder.make().add_assignment_in_x_weeks(weeks=1, **kwargs)


class PeriodBuilder(BaseNodeBuilderBase):
    object_attribute_name = 'period'
    modelcls = Period

    def __init__(self, *args, **kwargs):
        relatedstudents = kwargs.pop('relatedstudents', None)
        relatedexaminers = kwargs.pop('relatedexaminers', None)
        super(PeriodBuilder, self).__init__(*args, **kwargs)
        if relatedstudents:
            self.add_relatedstudents(*relatedstudents)
        if relatedexaminers:
            self.add_relatedexaminers(*relatedexaminers)

    @classmethod
    def quickadd_ducku_duck1010_active(cls):
        return SubjectBuilder.quickadd_ducku_duck1010() \
            .add_6month_active_period()

    def add_assignment(self, *args, **kwargs):
        kwargs['parentnode'] = self.period
        if 'first_deadline' not in kwargs:
            kwargs['first_deadline'] = timezone.now()
        return AssignmentBuilder(*args, **kwargs)

    def add_assignment_x_weeks_ago(self, weeks, **kwargs):
        kwargs['publishing_time'] = arrow.get(timezone.now()).replace(weeks=-weeks).datetime
        return self.add_assignment(**kwargs)

    def add_assignment_in_x_weeks(self, weeks, **kwargs):
        kwargs['publishing_time'] = arrow.get(timezone.now()).replace(weeks=+weeks).datetime
        return self.add_assignment(**kwargs)

    def add_relatedstudents(self, *users):
        relatedstudents = []
        for user in users:
            if isinstance(user, RelatedStudent):
                relatedstudent = user
            else:
                relatedstudent = RelatedStudent(
                    user=user)
            relatedstudent.period = self.period
            relatedstudents.append(relatedstudent)
        RelatedStudent.objects.bulk_create(relatedstudents)
        return self

    def add_relatedexaminers(self, *users):
        relatedexaminers = []
        for user in users:
            if isinstance(user, RelatedExaminer):
                relatedexaminer = user
            else:
                relatedexaminer = RelatedExaminer(
                    user=user)
            relatedexaminer.period = self.period
            relatedexaminers.append(relatedexaminer)
        RelatedExaminer.objects.bulk_create(relatedexaminers)
        return self

    @classmethod
    def make(cls, **kwargs):
        return SubjectBuilder.make().add_period(**kwargs)


class SubjectBuilder(BaseNodeBuilderBase):
    object_attribute_name = 'subject'
    modelcls = Subject

    @classmethod
    def quickadd_ducku_duck1010(cls, **kwargs):
        return SubjectBuilder('duck1010', **kwargs)

    def add_period(self, *args, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' not in kwargs:
            kwargs['start_time'] = arrow.get(timezone.now()).replace(days=-(30 * 3)).datetime
        if 'end_time' not in kwargs:
            kwargs['end_time'] = arrow.get(timezone.now()).replace(days=30 * 3).datetime
        return PeriodBuilder(*args, **kwargs)

    def add_6month_active_period(self, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' in kwargs or 'end_time' in kwargs:
            raise ValueError(
                'add_6month_active_period does not accept ``start_time`` or ``end_time`` as kwargs, it sets them automatically.')
        kwargs['start_time'] = arrow.get(timezone.now()).replace(days=-(30 * 3)).datetime
        kwargs['end_time'] = arrow.get(timezone.now()).replace(days=30 * 3).datetime
        if not 'short_name' in kwargs:
            kwargs['short_name'] = 'active'
        return self.add_period(**kwargs)

    def add_6month_lastyear_period(self, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' in kwargs or 'end_time' in kwargs:
            raise ValueError(
                'add_6month_lastyear_period does not accept ``start_time`` or ``end_time`` as kwargs, it sets them automatically.')
        kwargs['start_time'] = arrow.get(timezone.now()).replace(days=-(365 + 30 * 3)).datetime
        kwargs['end_time'] = arrow.get(timezone.now()).replace(days=-(365 - 30 * 3)).datetime
        if not 'short_name' in kwargs:
            kwargs['short_name'] = 'lastyear'
        return self.add_period(**kwargs)

    def add_6month_nextyear_period(self, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' in kwargs or 'end_time' in kwargs:
            raise ValueError(
                'add_6month_nextyear_period does not accept ``start_time`` or ``end_time`` as kwargs, it sets them automatically.')
        kwargs['start_time'] = arrow.get(timezone.now()).replace(days=365 - 30 * 3).datetime
        kwargs['end_time'] = arrow.get(timezone.now()).replace(days=365 + 30 * 3).datetime
        if not 'short_name' in kwargs:
            kwargs['short_name'] = 'nextyear'
        return self.add_period(**kwargs)

    @classmethod
    def make(cls, **kwargs):
        return SubjectBuilder(**kwargs)
