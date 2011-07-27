import logging
import itertools
from random import randint
from datetime import datetime, timedelta

from devilry.apps.gradeeditors.models import Config
from django.contrib.auth.models import User
from devilry.apps.core.models import Delivery
from devilry.apps.core.testhelpers import create_from_path


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

def autocreate_feedback(delivery, group_quality_percent, max_percent, grade_maxpoints):
    grade_percent = randint(group_quality_percent, max_percent)
    points = int(round(grade_maxpoints*grade_percent / 100.0))

    assignment = delivery.deadline.assignment_group.parentnode
    examiner = delivery.deadline.assignment_group.examiners.all()[0]
    feedback = delivery.feedbacks.create(rendered_view="Some text here:)",
                                         saved_by=examiner, points=points,
                                         grade="g{0}".format(points),
                                         is_passing_grade=bool(points))
    logging.info('        Feedback: points={points}, is_passing_grade={is_passing_grade}'.format(**feedback.__dict__))
    return feedback

def autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints):
    for x in xrange(randint(1, 3)):
        autocreate_feedback(delivery, group_quality_percent, max_percent, grade_maxpoints)


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
    #group.deadlines.create(deadline=deadline)
    logging.info("Created {0} (id:{1})".format(group, group.id))
    return group

def create_example_deliveries_and_feedback(group, quality_percents,
                                           group_quality_percent,
                                           grade_maxpoints,
                                           deliverycountrange,
                                           deadline):
    group.deadlines.create(deadline=deadline)
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
        logging.info("        Deliveries: {numdeliveries}".format(numdeliveries=numdeliveries))
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
        logging.info("        Very old deadline (14 days +): Only 3% missing feedback (forgotten)")
        if randint(0, 100) <= 3: # Always a 3% chance to forget giving feedback.
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Less than two weeks but more that 5 days since deadline
    elif deadline < five_days_ago:
        logging.info("        Old deadline (5-14 days): 10% of them has no feedback yet")
        if randint(0, 100) <= 10:
            # 10% of them has no feedback yet
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Recent deadline (2-5 days since deadline)
    # in the middle of giving feedback
    elif deadline < two_days_ago:
        logging.info("        Recent deadline (2-5 days): 50% of them has no feedback yet")
        if randint(0, 100) <= 50:
            # Half of them has no feedback yet
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Very recent deadline (0-2 days since deadline)
    elif deadline < now:
        logging.info("        Very recent deadline (0-3 days): 90% of them has no feedback yet")
        if randint(0, 100) <= 90:
            # 90% of them has no feedback yet
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Deadline is in the future
    else:
        logging.info("        Deadline is in the future. Made deliveries, but "\
                "no feedback")
        pass # No feedback

def parse_deadline_profile(profile):
    if not (profile.startswith("-") or profile.startswith("+")):
        raise SystemExit("Invalid --deadline-profile")

    now = datetime.now()
    if not profile[1:].isdigit():
        raise SystemExit("Numeric deadline profile must be + or - "\
                "suffixed with a number")
    days = int(profile[1:])
    if profile.startswith("-"):
        deadline = now - timedelta(days=int(days))
    else:
        deadline = now + timedelta(days=int(days))
    return deadline

def parse_deadline_profiles(profiles):
    return [parse_deadline_profile(profile) for profile in profiles.split(',')]


def create_assignment(period, short_name, long_name, deadlines):
    """ Create an assignment from path. """
    assignment = period.assignments.create(short_name=short_name,
                                           long_name=long_name,
                                           publishing_time = deadlines[0] - timedelta(14))
    Config.objects.create(assignment=assignment,
                          gradeeditorid='asminimalaspossible',
                          config='')
    #assignment.save()
    return assignment

def fit_assignment_in_parentnode(assignment, deadlines):
    """ Make sure assignment fits in parentnode """
    if assignment.parentnode.start_time > assignment.publishing_time:
        assignment.parentnode.start_time = assignment.publishing_time - \
                timedelta(days=5)
        assignment.parentnode.save()
    if assignment.parentnode.end_time < deadlines[-1]:
        assignment.parentnode.end_time = deadlines[-1] + timedelta(days=20)
        assignment.parentnode.save()


def grouplist(lst, n):
    l = len(lst)/n
    if len(lst)%n:
        l += 1
    for i in xrange(l):
        yield lst[i*n:i*n+n]

def create_groups(assignment,
                  deadlines, groupname_prefix,
                  all_examiners, examiners_per_group,
                  all_students, students_per_group,
                  deliverycountrange, grade_maxpoints):
    quality_percents = (
            93, # A > 93
            80, # B > 80
            65, # C > 65
            45, # D > 45
            30) # E > 30 

    examinersiter = itertools.cycle(grouplist(all_examiners, examiners_per_group))
    for studnum, students_in_group in enumerate(grouplist(all_students, students_per_group)):
        examiners_on_group = examinersiter.next()
        groupname = None
        if groupname_prefix:
            groupname = "%s %d" % (groupname_prefix, studnum)
        group = create_example_assignmentgroup(assignment, students_in_group,
                examiners_on_group, groupname)

        group_quality_percent = 100 - (float(studnum)/len(all_students)* 100)
        group_quality_percent = round(group_quality_percent)
        logging.debug("    Group quality percent: %s" % group_quality_percent)

        for deadline in deadlines:
            logging.info('    Deadline: {0}'.format(deadline))
            create_example_deliveries_and_feedback(group,
                                                   quality_percents,
                                                   group_quality_percent,
                                                   grade_maxpoints,
                                                   deliverycountrange,
                                                   deadline)

def create_numbered_users(numusers, prefix):
    users = ['{0}{1}'.format(prefix, number) for number in xrange(0, numusers)]
    create_missing_users(users)
    return users

def set_subject_and_period_long_name(assignment, subject_long_name, period_long_name):
    period = assignment.parentnode
    subject = period.parentnode
    period.long_name = period_long_name
    period.save()
    subject.long_name = subject_long_name
    subject.save()


def create_example_assignment(period, short_name, long_name,
                              pointscale = None, # TODO: Use this

                              groupname_prefix = None,
                              deadline_profiles = '-10',

                              num_students = 10,
                              studentname_prefix = 'student',
                              students_per_group = 1,

                              num_examiners=3,
                              examinername_prefix='examiner',
                              examiners_per_group=1,

                              grade_maxpoints=1,
                              deliverycountrange='0-4'):
    """
    :param subject_long_name: Long name of the subject.
    :param period_long_name: Long name of the period.
    :param groupname_prefix:
        Group name prefix. Group names will be this prefix plus
        a number. If this is None, group name will be left blank.
    :param deadline_profiles:
        A list of deadline offsets. Example: "+10,-20,-35" will create
        a deadline 10 days in the future, a deadline 20 days ago, and
        a deadline 35 days ago.

    :param num_students: Total number of students.
    :param studentname_prefix: Prefix of student name.
    :param students_per_group: Number of students per group.

    :param num_examiners: Total number of examiners.
    :param studentname_prefix: Prefix of student name.
    :param examiners_per_group: Number of examiners per group.

    :param grade_maxpoints: Maxpoints for grades.
    :param deliverycountrange:
            Number of deliveries. If it is a range separated by '-',
            a random number of deliveries in this range is used.
    """
    deadlines = parse_deadline_profiles(deadline_profiles)
    assignment = create_assignment(period, short_name, long_name, deadlines)

    fit_assignment_in_parentnode(assignment, deadlines)

    logging.info("Creating groups on {0}".format(assignment))
    all_examiners = create_numbered_users(num_examiners, examinername_prefix)
    all_students = create_numbered_users(num_students, studentname_prefix)
    create_groups(assignment,
                  deadlines = deadlines,
                  groupname_prefix = groupname_prefix,

                  all_examiners = all_examiners,
                  examiners_per_group = examiners_per_group,

                  all_students = all_students,
                  students_per_group = students_per_group,

                  grade_maxpoints = grade_maxpoints,
                  deliverycountrange = deliverycountrange)
