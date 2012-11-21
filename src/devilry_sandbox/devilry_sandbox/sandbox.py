from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import IntegrityError
from devilry.apps.core.models import Node
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from random import randint



STUDENT_SETS = {
                'duckburgh': [('dewey', 'Dewey Duck', 'group1'),
                              ('louie', 'Louie Duck', 'group1'),
                              ('huey', 'Huey Duck', 'group1'),
                              ('april', 'April Duck', 'group2'),
                              ('june', 'June Duck', 'group2'),
                              ('july', 'July Duck', 'group2')],
                'nordicgods': [('baldr', 'God of Beauty', 'group1'),
                               ('freyja', 'Goddess of Love', 'group1'),
                               ('freyr', 'God of Fertility', 'group1'),
                               ('kvasir', 'God of Inspiration', 'group1'),
                               ('loki', 'Trickster and god of Mischief', 'group2'),
                               ('thor', 'God of thunder and Battle', 'group2'),
                               ('odin', 'The "All Father"', 'group2')]
}


EXAMINER_SETS = {
                'duckburgh': [('donald', 'Donald Duck', 'group1'),
                              ('scrooge', 'Scrooge McDuck', 'group2')]
}



class LiveSandbox(object):
    def __init__(self, adminusername, adminfullname, prefix='sandbox'):
        self.prefix = prefix
        self.adminuser = self.createUser(adminusername, adminfullname)
        self.unique_key = self.adminuser.id

    def rootnode_exists(self):
        return Node.objects.filter(short_name=self.prefix).exists()

    def create_rootnode_if_not_exists(self):
        if not self.rootnode_exists():
            node = Node.objects.create(short_name=self.prefix,
                                       long_name=self.prefix)
        else:
            node = Node.objects.get(short_name=self.prefix)
        return node

    def createUser(self, username, fullname):
        user = User.objects.create(username=username,
                                   email='{0}@example.com'.format(username))
        user.devilryuserprofile.full_name = fullname
        user.devilryuserprofile.save()
        user.set_password('test')
        user.save()
        return user

    def uniquewrap(self, s):
        return '{0}{1}_{2}'.format(self.prefix, self.unique_key, s)

    def addOrGetUser(self, username, fullname):
        try:
            username = self.uniquewrap(username)
            user = self.createUser(username, fullname)
        except IntegrityError:
            return User.objects.get(username=username)
        else:
            return user

    def add_relatedstudents(self, period, *sets):
        for setname in sets:
            users = STUDENT_SETS[setname]
            for username, fullname, tags in users:
                period.relatedstudent_set.create(user=self.addOrGetUser(username, fullname),
                                                 candidate_id=str(randint(0, 10000000)),
                                                 tags=tags)

    def add_relatedexaminers(self, period, *sets):
        for setname in sets:
            users = EXAMINER_SETS[setname]
            for username, fullname, tags in users:
                period.relatedexaminer_set.create(user=self.addOrGetUser(username, fullname),
                                                  tags=tags)


    def create_subject(self, short_name, long_name):
        node = self.create_rootnode_if_not_exists()
        subject = node.subjects.create(short_name=short_name,
                                      long_name=long_name)
        return subject

    def create_period(self, subject, short_name, long_name,
                      student_sets=['duckburgh', 'nordicgods'],
                      examiner_sets=['duckburgh']):
        period = subject.periods.create(short_name=self.uniquewrap(short_name),
                                        long_name=long_name,
                                        start_time=datetime.now() - timedelta(days=90),
                                        end_time=datetime.now() + timedelta(days=120))
        period.admins.add(self.adminuser)
        self.add_relatedstudents(period, *student_sets)
        self.add_relatedexaminers(period, *examiner_sets)
        return period
