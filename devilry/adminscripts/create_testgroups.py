from optparse import OptionParser
import logging
import itertools

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
            usage = "%prog [options] <assignment-id>")
    add_settings_option(p)
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
                User(username=username).save()
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

    def autocreate_feedback(delivery):
        feedback = delivery.get_feedback()
        assignment = delivery.assignment_group.parentnode
        gradeplugin = assignment.get_gradeplugin_registryitem().model_cls
        examplegrade = gradeplugin.get_example_xmlrpcstring(assignment, 5)

        feedback.set_grade_from_xmlrpcstring(examplegrade)
        feedback.text = "Very good:)"
        feedback.published = True
        examiner = delivery.assignment_group.examiners.all()[0]
        feedback.last_modified_by = examiner
        feedback.save()

    assignment = args[0]
    groupnameprefix = None
    student_prefix = "student"
    examiner_prefix = "examiner"
    num_examiners = 11
    examiners_per_group = 3

    examiners = ['%s%d' % (examiner_prefix, d)
            for d in xrange(0,num_examiners)]
    students = ['%s%d' % (student_prefix, d) for d in xrange(1,30)]
    create_missing_users(itertools.chain(students, examiners))

    examinersiter = itertools.cycle(group(examiners, examiners_per_group))
    for username in students:
        path = "%s.%s" % (assignment, username)
        logging.info("Creating %s" % path)
        group = create_from_path(path,
                grade_plugin_key='grade_rstschema:rstschemagrade')
        group.save()
        group.parentnode.get_gradeplugin_registryitem().model_cls.init_example(
                assignment, 8)
        for examiner in examinersiter.next():
            group.examiners.add(User.objects.get(username=examiner))
        delivery = autocreate_delivery(group)
        autocreate_feedback(delivery)
