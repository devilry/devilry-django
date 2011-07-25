#!/usr/bin/env python

from optparse import OptionParser
import logging
import itertools
from random import randint
from datetime import datetime, timedelta

from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)

def grouplist(lst, n):
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
            default=50, type='int',
            help="Number of students. Defaults to 10.")
    p.add_option("-e", "--num-examiners", dest="num_examiners",
            default=3, type='int',
            help="Number of examiners. Defaults to 3.")
    p.add_option("--groupname-prefix", dest="groupname_prefix",
            default=None,
            help="Group name prefix. Group names will be this prefix plus "\
                    "a number. If you dont spesify this, group name will "\
                    "be blank.")
    p.add_option("--subject-long-name", dest="subject_long_name",
            default=None,
            help="The long name of the subject. Defaults to short name"\
                "capitalized")
    p.add_option("--period-long-name", dest="period_long_name",
            default=None,
            help="The long name of the period. Defaults to short name"\
                "capitalized")
    p.add_option("--assignment-long-name", dest="assignment_long_name",
            default=None,
            help="The long name of the assignment. Defaults to short name"\
                "capitalized")
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
    p.add_option("-g", "--grade-maxpoints", dest="grade_maxpoints",
            default=1, type='int',
            help="Maximum number of points possible on the assignment. "\
                "Groups will get a random score between 0 and this number. "
                "Defaults to 1.")
    p.add_option("--pointscale", dest="pointscale",
            default=None, type='int',
            help="The pointscale of the assignment. Default is "\
                    "no pointscale.")
    p.add_option("--deliverycountrange", default='0-4',
                 dest='deliverycountrange',
                 help=("Number of deliveries. If it is a range separated by '-', "
                       "a random number of deliveries in this range is used. Defaults "
                       "to '0-4'"))
    p.add_option("--grade-plugin", dest="gradeplugin",
            default=None, help="Grade plugin key.")
    p.add_option("-p", "--deadline-profile", dest="deadline_profile",
            default='recent',
            help="Deadline profile. Defaults to 'recent' "
                "Values: soon (no feedback, but 50% deliveries), "\
                "very-recent (some feedback), recent (about " \
                "50% feedback), old (about 90% feedback), very-old (all have " \
                "feedback). In addition, there is always some bad students " \
                "who forget to deliver, and some bad examiners who forget to " \
                "publish and correct.")
    p.add_option("--deadline", dest="deadline",
            default=None,
            help="Deadline. If this is specified, --deadline-profile is "\
                "ignored. Format: YYYY-MM-DD. Time will always be 00:00.")
    p.add_option("--pubtime-diff", dest="pubtime_diff",
            default=14, type='int',
            help="Number of days between publishing time and deadline. "\
                "Defaults to 14.")


    add_quiet_opt(p)
    add_debug_opt(p)
    (opt, args) = p.parse_args()
    setup_logging(opt)

    # Django must be imported after setting DJANGO_SETTINGS_MODULE
    set_django_settings_module(opt)
    load_devilry_plugins()
    from django.contrib.auth.models import User
    from devilry.apps.core.models import Delivery
    from devilry.apps.core.testhelpers import create_from_path

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
                u = User(username=username, email="%s@example.com" % username)
                u.set_password("test")
                u.save()
                logging.info("Created user %s." % username)

    def autocreate_delivery(group):
        active_deadline = group.get_active_deadline()

        cand = group.candidates.all()[0]
        delivery = active_deadline.deliveries.create(delivered_by=cand, successful=True)
        delivery.add_file('helloworld.txt', ['hello cruel world'])
        delivery.add_file('helloworld.py', ['print "hello world"'])
        delivery.add_file('helloworld.java', [
            '// Too much code for a sane "hello world"'])

        others = Delivery.objects.filter(deadline__assignment_group=group).order_by("-number")
        if others.count() == 1:
            if active_deadline.deadline < datetime.now():
                if randint(0, 100) <= 5:
                    # 5% chance to get the first delivery after the deadline
                    offset = timedelta(minutes=-randint(1, 20))
                else:
                    offset = timedelta(hours=randint(0, 15),
                            minutes=randint(0, 59))
                delivery.time_of_delivery = active_deadline.deadline - offset
            else:
                # Deadline is in the future. Deliver a random time before
                # "now". They can not deliver more than 5 deliveries (see
                # create_example_deliveries_and_feedback), so if
                # we say 5*3 hours in the past as a minimum for the first
                # delivery, we will never get deliveries in the future
                offset = timedelta(hours=randint(15, 25),
                        minutes=randint(0, 59))
                delivery.time_of_delivery = datetime.now() - offset
        else:
            # Make sure deliveries are sequential
            last_delivery = others[1].time_of_delivery
            delivery.time_of_delivery = last_delivery + \
                    timedelta(hours=randint(0, 2), minutes=randint(0,
                        59))
        delivery.save()
        return delivery

    def autocreate_deliveries(group, numdeliveries):
        d = []
        for x in xrange(numdeliveries):
            d.append(autocreate_delivery(group))
        return d

    def autocreate_feedback(delivery, group_quality_percent, max_percent):
        grade_percent = randint(group_quality_percent, max_percent)
        points = int(round(grade_maxpoints*grade_percent / 100.0))

        assignment = delivery.deadline.assignment_group.parentnode
        examiner = delivery.deadline.assignment_group.examiners.all()[0]
        feedback = delivery.feedbacks.create(rendered_view="Some text here:)",
                                             saved_by=examiner, points=points,
                                             grade="g{0}".format(points),
                                             is_passing_grade=bool(points))
        logging.info('    Feedback: points={points}, is_passing_grade={is_passing_grade}'.format(**feedback.__dict__))
        return feedback

    def autocreate_feedbacks(delivery, group_quality_percent, max_percent):
        for x in xrange(randint(1, 3)):
            autocreate_feedback(delivery, group_quality_percent, max_percent)


    def create_example_assignmentgroup(assignment, students, examiners,
            groupname=None):
        """ Create a assignmentgroup with the given students and examiners.

        :param assignment: The :class:`devilry.core.models.Assignment` where
            you wish to create the group.
        :param students: List of usernames.
        :param examiners: List of usernames.
        :return: The created :class:`devilry.core.models.AssignmentGroup`.
        """
        group = assignment.assignmentgroups.create()
        for student in students:
            group.candidates.create(
                    student=User.objects.get(username=student))
        for examiner in examiners:
            group.examiners.add(User.objects.get(username=examiner))
        fakedeadline = group.deadlines.all()[0]
        fakedeadline.deadline = datetime(1970, 1, 1)
        group.deadlines.create(deadline=deadline)
        logging.info("Created {0} (id:{1})".format(group, group.id))
        return group

    def create_example_deliveries_and_feedback(group, quality_percents,
                                               group_quality_percent,
                                               grade_maxpoints,
                                               deliverycountrange):
        deadline = group.get_active_deadline().deadline
        now = datetime.now()
        two_weeks_ago = now - timedelta(days=14)
        two_days_ago = now - timedelta(days=2)
        five_days_ago = now - timedelta(days=5)

        # Deadline in the future - about half has not yet delivered - no
        # feedback
        if deadline > now:
            if randint(0, 100) <= 50:
                logging.debug("Deadline in the future - not made "\
                        "any deliveries yet")
                return

        # Every C student and worst has a 5% chance of forgetting to
        # deliver
        elif group_quality_percent < quality_percents[1]:
            if randint(0, 100) <= 5:
                return

        numdeliveries = 1
        deliverycountrange_split = deliverycountrange.split('-', 1)
        if len(deliverycountrange) > 1:
            numdeliveries = randint(int(deliverycountrange_split[0]),
                                    int(deliverycountrange_split[1]))
        else:
            numdeliveries = int(deliverycountrange[0])
        if numdeliveries == 0:
            return
        else:
            logging.info('    Deliveries: {numdeliveries}'.format(numdeliveries=numdeliveries))
        deliveries = autocreate_deliveries(group, numdeliveries)
        delivery = deliveries[-1]

        # Determine grade. Everyone get a random grade within their "usual"
        # grade.
        max_percent = 100
        for p in quality_percents:
            if group_quality_percent > p:
                break
            max_percent = p

        # More than two weeks since deadline - should have feedback on about all
        if deadline < two_weeks_ago:
            logging.info("    Very old deadline (14 days +)")
            if randint(0, 100) <= 3: # Always a 3% chance to forget giving feedback.
                return
            autocreate_feedbacks(delivery, group_quality_percent, max_percent)

        # Less than two weeks but more that 5 days since deadline
        elif deadline < five_days_ago:
            logging.info("    Old deadline (5-14 days)")
            if randint(0, 100) <= 10:
                # 10% of them has no feedback yet
                return
            autocreate_feedbacks(delivery, group_quality_percent, max_percent)

        # Recent deadline (2-5 days since deadline)
        # in the middle of giving feedback
        elif deadline < two_days_ago:
            logging.info("    Recent deadline (2-5 days)")
            if randint(0, 100) <= 50:
                # Half of them has no feedback yet
                return
            autocreate_feedbacks(delivery, group_quality_percent, max_percent)

        # Very recent deadline (0-2 days since deadline)
        elif deadline < now:
            logging.info("    Very recent deadline (0-3 days)")
            if randint(0, 100) <= 90:
                # 90% of them has no feedback yet
                return
            autocreate_feedbacks(delivery, group_quality_percent, max_percent)

        # Deadline is in the future
        else:
            logging.info("    Deadline is in the future. Made deliveries, but "\
                    "no feedback")
            pass # No feedback



    assignmentpath = args[0]
    groupname_prefix = opt.groupname_prefix
    student_prefix = opt.studentname_prefix
    students_per_group = opt.students_per_group
    num_students = opt.num_students
    examiner_prefix = opt.examinername_prefix
    num_examiners = opt.num_examiners
    examiners_per_group = opt.examiners_per_group
    grade_maxpoints = opt.grade_maxpoints
    deliverycountrange = opt.deliverycountrange
    #print deliverycountrange

    ## NOTE: Not used anymore because of grade editors
    #if not opt.gradeplugin:
        #raise SystemExit("--grade-plugin is required. Possible values: %s" %
                #', '.join(['"%s"' % key for key, i in registry.iteritems()]))
    #gradeplugin = opt.gradeplugin

    if opt.deadline:
        deadline = datetime.strptime(opt.deadline, "%Y-%m-%d")
    else:
        now = datetime.now()
        p = opt.deadline_profile
        if p == 'soon':
            deadline = now + timedelta(days=1)
        elif p == 'very-recent':
            deadline = now - timedelta(days=1)
        elif p == 'recent':
            deadline = now - timedelta(days=3)
        elif p == 'old':
            deadline = now - timedelta(days=9)
        elif p == 'very-old':
            deadline = now - timedelta(days=60)
        elif p.startswith("-") or p.startswith("+"):
            if not p[1:].isdigit():
                raise SystemExit("Numeric deadline profile must be + or - "\
                        "suffixed with a number")
            days = int(p[1:])
            if p.startswith("-"):
                deadline = now - timedelta(days=int(days))
            else:
                deadline = now + timedelta(days=int(days))
        else:
            raise SystemExit("Invalid --deadline-profile")


    examiners = ['%s%d' % (examiner_prefix, d)
            for d in xrange(0,num_examiners)]
    all_students = ['%s%d' % (student_prefix, d) for d in xrange(0, num_students)]
    create_missing_users(itertools.chain(all_students, examiners))

    # Create the assignment
    assignment = create_from_path(assignmentpath)
    assignment.publishing_time = deadline - timedelta(days=opt.pubtime_diff)
    if opt.pointscale:
        assignment.autoscale = False
        assignment.pointscale = opt.pointscale
    if opt.assignment_long_name:
        assignment.long_name = opt.assignment_long_name
    assignment.save()

    # Make sure assignment fits in parentnode
    if assignment.parentnode.start_time > assignment.publishing_time:
        assignment.parentnode.start_time = assignment.publishing_time - \
                timedelta(days=5)
        assignment.parentnode.save()
    if assignment.parentnode.end_time < deadline:
        assignment.parentnode.end_time = deadline + timedelta(days=20)
        assignment.parentnode.save()
    logging.info(
            "Creating groups on %s with deadline %s" % (
                assignment, deadline))

    # Subject and period
    period = assignment.parentnode
    subject = period.parentnode
    if opt.period_long_name:
        period.long_name = opt.period_long_name
        period.save()
    if opt.subject_long_name:
        subject.long_name = opt.subject_long_name
        subject.save()


    examinersiter = itertools.cycle(grouplist(examiners, examiners_per_group))
    quality_percents = (
            93, # A > 93
            80, # B > 80
            65, # C > 65
            45, # D > 45
            30) # E > 30 
    for studnum, students in enumerate(grouplist(all_students, students_per_group)):
        examiners = examinersiter.next()
        groupname = None
        if groupname_prefix:
            groupname = "%s %d" % (groupname_prefix, studnum)
        group = create_example_assignmentgroup(assignment, students,
                examiners, groupname)

        group_quality_percent = 100 - (float(studnum)/num_students * 100)
        group_quality_percent = round(group_quality_percent)
        logging.debug("Group quality percent: %s" % group_quality_percent)
        create_example_deliveries_and_feedback(group, quality_percents,
                group_quality_percent, grade_maxpoints, deliverycountrange)
