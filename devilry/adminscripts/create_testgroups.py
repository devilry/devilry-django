from optparse import OptionParser
import logging
import itertools
from random import randint

from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)

def group(lst, n):
    l = len(lst)/n
    if len(lst)%n:
        l += 1
    for i in xrange(l):
        yield lst[i*n:i*n+n]


if __name__ == "__main__":

    p = OptionParser(
            usage = "%prog [options] <assignment-path>")
    add_settings_option(p)
    p.add_option("-s", "--num-students", dest="num_students",
            default=10, type='int',
            help="Number of students. Defaults to 10.")
    p.add_option("-e", "--num-examiners", dest="num_examiners",
            default=3, type='int',
            help="Number of examiners. Defaults to 3.")
    p.add_option("--groupname-prefix", dest="groupname_prefix",
            default=None,
            help="Group name prefix. Group names will be this prefix plus "\
                    "a number. If you dont spesify this, group name will "\
                    "be blank.")
    p.add_option("--student-name-prefix", dest="studentname_prefix",
            default="student",
            help="Student name prefix. Student names will be this prefix "\
                    "plus a number. Defaults to 'student'")
    p.add_option("--students-per-group", dest="students_per_group",
            default=1, type='int',
            help="Number of students per group. Defaults to 1.")
    p.add_option("--examiner-name-prefix", dest="examinername_prefix",
            default="examiner",
            help="Examiner name prefix. Examiner names will be this prefix "\
                    "plus a number. Defaults to 'examiner'")
    p.add_option("--examiners-per-group", dest="examiners_per_group",
            default=1, type='int',
            help="Number of examiners per group. Defaults to 1.")
    p.add_option("--grade-maxpoints", dest="grade_maxpoints",
            default=1, type='int',
            help="Maximum number of points possible on the assignment. "\
                "Groups will get a random score between 0 and this number. "
                "Defaults to 1.")
    p.add_option("--grade-plugin", dest="gradeplugin",
            default=None,
            help="Grade plugin. Defaults to the one specified in "\
                    "settings.py.")
    add_quiet_opt(p)
    add_debug_opt(p)
    (opt, args) = p.parse_args()
    setup_logging(opt)

    # Django must be imported after setting DJANGO_SETTINGS_MODULE
    set_django_settings_module(opt)
    load_devilry_plugins()
    from django.contrib.auth.models import User
    from devilry.core.models import Delivery
    from devilry.core.testhelpers import create_from_path
    from devilry.core.gradeplugin import registry

    def exit_help():
        p.print_help()
        raise SystemExit()
    if len(args) != 1:
        exit_help()
    setup_logging(opt)

    def create_missing_users(usernames):
        for username in usernames:
            try:
                User.objects.get(username=username)
                logging.debug("User %s already exists." % username)
            except User.DoesNotExist, e:
                u = User(username=username)
                u.set_password("test")
                u.save()
                logging.info("Created user %s." % username)

    def autocreate_delivery(group):
        student = group.candidates.all()[0].student
        delivery = Delivery.begin(group, student)
        delivery.add_file('helloworld.txt', ['hello cruel world'])
        delivery.add_file('helloworld.py', ['print "hello world"'])
        delivery.add_file('helloworld.java', [
            '// Too much code for a sane "hello world"'])
        delivery.finish()
        return delivery

    def autocreate_feedback(delivery, maxpoints, published):
        assignment = delivery.assignment_group.parentnode
        feedback = delivery.get_feedback()
        feedback.text = "Very good:)"
        feedback.published = published
        examiner = delivery.assignment_group.examiners.all()[0]
        feedback.last_modified_by = examiner
        gradeplugin = assignment.get_gradeplugin_registryitem().model_cls
        examplegrade = gradeplugin.get_example_xmlrpcstring(assignment,
                randint(0, maxpoints))
        feedback.set_grade_from_xmlrpcstring(examplegrade)
        feedback.save()


    assignment = args[0]
    groupname_prefix = opt.groupname_prefix
    student_prefix = opt.studentname_prefix
    students_per_group = opt.students_per_group
    num_students = opt.num_students
    examiner_prefix = opt.examinername_prefix
    num_examiners = opt.num_examiners
    examiners_per_group = opt.examiners_per_group
    grade_maxpoints = opt.grade_maxpoints
    gradeplugin = opt.gradeplugin or registry.getdefaultkey()

    examiners = ['%s%d' % (examiner_prefix, d)
            for d in xrange(0,num_examiners)]
    students = ['%s%d' % (student_prefix, d) for d in xrange(0, num_students)]
    create_missing_users(itertools.chain(students, examiners))

    examinersiter = itertools.cycle(group(examiners, examiners_per_group))
    for i, usernames in enumerate(group(students, students_per_group)):
        path = "%s.%s" % (assignment, ",".join(usernames))
        logging.info("Creating %s" % path)
        group = create_from_path(path,
                grade_plugin_key=gradeplugin)
        if groupname_prefix:
            group.name = "%s %d" % (groupname_prefix, i)
        group.save()
        group.parentnode.get_gradeplugin_registryitem().model_cls.init_example(
                group.parentnode, grade_maxpoints)
        for examiner in examinersiter.next():
            group.examiners.add(User.objects.get(username=examiner))
        num = randint(0, 10)
        if num > 2:
            delivery = autocreate_delivery(group)
            if num > 4:
                autocreate_feedback(delivery, grade_maxpoints,
                        num > 6)
