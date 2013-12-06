from django.contrib.auth.models import User

from devilry.apps.core.models import Node
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Deadline
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import FileMeta

from .datebuilder import DateTimeBuilder


class ReloadableDbBuilderInterface(object):
    def update(self, **attributes):
        raise NotImplementedError()

    def reload_from_db(self):
        raise NotImplementedError()


class UserBuilder(ReloadableDbBuilderInterface):
    def __init__(self, username, full_name=None, email=None):
        self.user = User(username=username, email=email)
        self.user.set_password('test')
        self.user.full_clean()
        self.user.save()
        if full_name:
            profile = self.user.get_profile()
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
        for attrname, value in attributes.iteritems():
            setattr(self.node, attrname, value)
        self._save()
        self.reload_from_db()

    def reload_from_db(self):
        obj = getattr(self, self.object_attribute_name)
        setattr(self, self.object_attribute_name, obj.__class__.objects.create(pk=obj.pk))


class BaseNodeBuilderBase(CoreBuilderBase):
    modelcls = None

    def __init__(self, short_name, long_name=None, **kwargs):
        full_kwargs = {
            'short_name': short_name,
            'long_name': long_name or short_name
        }
        full_kwargs.update(kwargs)
        setattr(self.object_attribute_name, self.modelcls.objects.create(**full_kwargs))



class FileMetaBuilder(CoreBuilderBase):
    def __init__(self, delivery, filename, data):
        self.filemeta = FileMeta.objects.create(delivery, filename=filename, size=0)
        f = FileMeta.deliverystore.write_open(self.filemeta)
        f.write(data)
        f.close()
        self.filemeta.size = len(data)
        self.filemeta.save()


class DeliveryBuilder(CoreBuilderBase):
    def __init__(self, **kwargs):
        self.delivery = Delivery.objects.create(**kwargs)

    def _save(self):
        self.delivery.save(autoset_time_of_delivery=False)

    def add_filemeta(self, **kwargs):
        kwargs['delivery'] = self.delivery
        return FileMetaBuilder(**kwargs)


class DeadlineBuilder(CoreBuilderBase):
    def __init__(self, **kwargs):
        self.deadline = Deadline.objects.create(**kwargs)

    def add_delivery(self, **kwargs):
        kwargs['deadline'] = self.deadline
        return DeliveryBuilder(**kwargs)

    def add_delivery_after_deadline(self, timedeltaobj, **kwargs):
        if 'time_of_delivery' in kwargs:
            raise ValueError('add_delivery_after_deadline does not accept ``time_of_delivery`` as kwarg, it sets it automatically.')
        kwargs['time_of_delivery'] = self.deadline.deadline + timedeltaobj
        return self.add_delivery(**kwargs)

    def add_delivery_before_deadline(self, timedeltaobj, **kwargs):
        if 'time_of_delivery' in kwargs:
            raise ValueError('add_delivery_before_deadline does not accept ``time_of_delivery`` as kwarg, it sets it automatically.')
        kwargs['time_of_delivery'] = self.deadline.deadline - timedeltaobj
        return self.add_delivery(**kwargs)


class GroupBuilder(CoreBuilderBase):
    def __init__(self, students=[], candidates=[], examiners=[], **kwargs):
        self.group = AssignmentGroup.objects.create(**kwargs)
        if students and candidates:
            raise ValueError('Provide one of ``students`` or ``candidates``.')
        self.add_students(*students)
        self.add_candidates(*candidates)
        self.add_examiners(*examiners)

    def add_students(self, *users):
        for user in users:
            self.group.students.create(student=user)
        return self

    def add_candidates(self, *candidates):
        for candidate in candidates:
            self.group.students.add(candidate)
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

    def add_group(self, *args, **kwargs):
        kwargs['parentnode'] = self.assignment
        return GroupBuilder(*args, **kwargs)



class PeriodBuilder(CoreBuilderBase):
    object_attribute_name = 'period'
    modelcls = Period

    def add_assignment(self, *args, **kwargs):
        kwargs['parentnode'] = self.period
        return AssignmentBuilder(*args, **kwargs)


class SubjectBuilder(CoreBuilderBase):
    object_attribute_name = 'subject'
    modelcls = Subject

    def add_period(self, *args, **kwargs):
        kwargs['parentnode'] = self.subject
        return PeriodBuilder(*args, **kwargs)


class NodeBuilder(CoreBuilderBase):
    object_attribute_name = 'node'
    modelcls = Node

    def add_subject(self, *args, **kwargs):
        kwargs['parentnode'] = self.node
        return SubjectBuilder(*args, **kwargs)
