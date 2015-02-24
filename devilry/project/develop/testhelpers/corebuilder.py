from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta
from django.core.files.base import ContentFile

from devilry.apps.core.models import Node, StaticFeedbackFileAttachment
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Deadline
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.models import FileMeta
from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.deliverystore import MemoryDeliveryStore
from .datebuilder import DateTimeBuilder


class ReloadableDbBuilderInterface(object):
    def update(self, **attributes):
        raise NotImplementedError()

    def reload_from_db(self):
        raise NotImplementedError()


class UserBuilder(ReloadableDbBuilderInterface):
    def __init__(self, username, full_name=None, email=None, is_superuser=False, is_staff=False):
        email = email or u'{}@example.com'.format(username)
        self.user = User(username=username, email=email,
            is_superuser=is_superuser, is_staff=is_staff)
        self.user.set_password('test')
        self.user.full_clean()
        self.user.save()
        profile = self.user.get_profile()
        if full_name:
            profile.full_name = full_name
        profile.save()

    def update(self, **attributes):
        for attrname, value in attributes.iteritems():
            setattr(self.user, attrname, value)
        self.user.save()
        self.reload_from_db()

    def update_profile(self, **attributes):
        profile = self.user.get_profile()
        for attrname, value in attributes.iteritems():
            setattr(profile, attrname, value)
        profile.save()
        self.reload_from_db()

    def reload_from_db(self):
        self.user = User.objects.get(id=self.user.id)



class CoreBuilderBase(ReloadableDbBuilderInterface):
    object_attribute_name = None

    def _save(self):
        getattr(self, self.object_attribute_name).save()

    def update(self, **attributes):
        obj = getattr(self, self.object_attribute_name)
        for attrname, value in attributes.iteritems():
            setattr(obj, attrname, value)
        self._save()
        self.reload_from_db()

    def reload_from_db(self):
        obj = getattr(self, self.object_attribute_name)
        setattr(self, self.object_attribute_name, obj.__class__.objects.get(pk=obj.pk))


class BaseNodeBuilderBase(CoreBuilderBase):
    modelcls = None

    def __init__(self, short_name, long_name=None, **kwargs):
        full_kwargs = {
            'short_name': short_name,
            'long_name': long_name or short_name
        }
        full_kwargs.update(kwargs)
        setattr(self, self.object_attribute_name, self.modelcls.objects.create(**full_kwargs))

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
            kwargs['time_of_delivery'] = datetime.now()
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
            raise ValueError('add_delivery_after_deadline does not accept ``time_of_delivery`` as kwarg, it sets it automatically.')
        kwargs['time_of_delivery'] = self.deadline.deadline + timedeltaobject
        return self.add_delivery(**kwargs)

    def add_delivery_before_deadline(self, timedeltaobject, **kwargs):
        if 'time_of_delivery' in kwargs:
            raise ValueError('add_delivery_before_deadline does not accept ``time_of_delivery`` as kwarg, it sets it automatically.')
        kwargs['time_of_delivery'] = self.deadline.deadline - timedeltaobject
        return self.add_delivery(**kwargs)

    def add_delivery_x_hours_after_deadline(self, hours, **kwargs):
        return self.add_delivery_after_deadline(timedelta(hours=hours), **kwargs)

    def add_delivery_x_hours_before_deadline(self, hours, **kwargs):
        return self.add_delivery_before_deadline(timedelta(hours=hours), **kwargs)


class AssignmentGroupBuilder(CoreBuilderBase):
    object_attribute_name = 'group'

    @classmethod
    def quickadd_ducku_duck1010_active_assignment1_group(cls, studentuser=None):
        students = []
        if studentuser:
            students.append(studentuser)
        return AssignmentBuilder\
            .quickadd_ducku_duck1010_active_assignment1()\
            .add_group(students=students)

    def __init__(self, students=[], candidates=[], examiners=[], **kwargs):
        self.group = AssignmentGroup.objects.create(**kwargs)
        self.add_students(*students)
        self.add_candidates(*candidates)
        self.add_examiners(*examiners)

    def add_students(self, *users):
        for user in users:
            self.group.candidates.create(student=user)
        return self

    def add_candidates(self, *candidates):
        for candidate in candidates:
            self.group.candidates.add(candidate)
        return self

    def add_examiners(self, *users):
        for user in users:
            self.group.examiners.create(user=user)
        return self

    def add_deadline(self, **kwargs):
        kwargs['assignment_group'] = self.group
        return DeadlineBuilder(**kwargs)

    def add_deadline_in_x_weeks(self, weeks, **kwargs):
        if 'deadline' in kwargs:
            raise ValueError('add_deadline_in_x_weeks does not accept ``deadline`` as kwarg, it sets it automatically.')
        kwargs['deadline'] = DateTimeBuilder.now().plus(weeks=weeks)
        return self.add_deadline(**kwargs)

    def add_deadline_x_weeks_ago(self, weeks, **kwargs):
        if 'deadline' in kwargs:
            raise ValueError('add_deadline_x_weeks_ago does not accept ``deadline`` as kwarg, it sets it automatically.')
        kwargs['deadline'] = DateTimeBuilder.now().minus(weeks=weeks)
        return self.add_deadline(**kwargs)


class AssignmentBuilder(BaseNodeBuilderBase):
    object_attribute_name = 'assignment'
    modelcls = Assignment

    @classmethod
    def quickadd_ducku_duck1010_active_assignment1(cls):
        return PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')

    def __init__(self, *args, **kwargs):
        if not 'publishing_time' in kwargs:
            kwargs['publishing_time'] = datetime.now()
        super(AssignmentBuilder, self).__init__(*args, **kwargs)

    def add_group(self, *args, **kwargs):
        kwargs['parentnode'] = self.assignment
        return AssignmentGroupBuilder(*args, **kwargs)


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
        return SubjectBuilder.quickadd_ducku_duck1010()\
            .add_6month_active_period()

    def add_assignment(self, *args, **kwargs):
        kwargs['parentnode'] = self.period
        return AssignmentBuilder(*args, **kwargs)

    def add_assignment_x_weeks_ago(self, weeks, **kwargs):
        kwargs['publishing_time'] = DateTimeBuilder.now().minus(weeks=weeks)
        return self.add_assignment(**kwargs)

    def add_assignment_in_x_weeks(self, weeks, **kwargs):
        kwargs['publishing_time'] = DateTimeBuilder.now().plus(weeks=weeks)
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


class SubjectBuilder(BaseNodeBuilderBase):
    object_attribute_name = 'subject'
    modelcls = Subject

    @classmethod
    def quickadd_ducku_duck1010(cls, **kwargs):
        return NodeBuilder('ducku').add_subject('duck1010', **kwargs)

    def add_period(self, *args, **kwargs):
        kwargs['parentnode'] = self.subject
        return PeriodBuilder(*args, **kwargs)

    def add_6month_active_period(self, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' in kwargs or 'end_time' in kwargs:
            raise ValueError('add_6month_active_period does not accept ``start_time`` or ``end_time`` as kwargs, it sets them automatically.')
        kwargs['start_time'] = DateTimeBuilder.now().minus(days=30*3)
        kwargs['end_time'] = DateTimeBuilder.now().plus(days=30*3)
        if not 'short_name' in kwargs:
            kwargs['short_name'] = 'active'
        return self.add_period(**kwargs)

    def add_6month_lastyear_period(self, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' in kwargs or 'end_time' in kwargs:
            raise ValueError('add_6month_lastyear_period does not accept ``start_time`` or ``end_time`` as kwargs, it sets them automatically.')
        kwargs['start_time'] = DateTimeBuilder.now().minus(days=365 + 30*3)
        kwargs['end_time'] = DateTimeBuilder.now().minus(days=365 - 30*3)
        if not 'short_name' in kwargs:
            kwargs['short_name'] = 'lastyear'
        return self.add_period(**kwargs)

    def add_6month_nextyear_period(self, **kwargs):
        kwargs['parentnode'] = self.subject
        if 'start_time' in kwargs or 'end_time' in kwargs:
            raise ValueError('add_6month_nextyear_period does not accept ``start_time`` or ``end_time`` as kwargs, it sets them automatically.')
        kwargs['start_time'] = DateTimeBuilder.now().plus(days=365 - 30*3)
        kwargs['end_time'] = DateTimeBuilder.now().plus(days=365 + 30*3)
        if not 'short_name' in kwargs:
            kwargs['short_name'] = 'nextyear'
        return self.add_period(**kwargs)


class NodeBuilder(BaseNodeBuilderBase):
    object_attribute_name = 'node'
    modelcls = Node

    @classmethod
    def quickadd_ducku(cls, **kwargs):
        return NodeBuilder('ducku')

    def add_subject(self, *args, **kwargs):
        kwargs['parentnode'] = self.node
        return SubjectBuilder(*args, **kwargs)

    def add_childnode(self, *args, **kwargs):
        kwargs['parentnode'] = self.node
        return NodeBuilder(*args, **kwargs)
