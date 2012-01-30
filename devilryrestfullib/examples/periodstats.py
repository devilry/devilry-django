import sys
from getpass import getpass
from devilryrestfullib import login, RestfulFactory, HttpResponseBadRequest
from os import linesep


####################################################################
# Parse input from user
####################################################################

if len(sys.argv) != 5:
    raise SystemExit('Usage: {0} <devilry-url> <username> <subject-short-name> <period-short-name>'.format(sys.argv[0]))

devilry_url = sys.argv[1]
username = sys.argv[2]
subject_short_name = sys.argv[3]
period_short_name = sys.argv[4]
password = getpass() # Ask user to input password
#password = 'test'


####################################################################
# Common for more or less any Devilry application
####################################################################

## Log in
login_url = '{0}/authenticate/login'.format(devilry_url)
logincookie = login(login_url, username=username, password=password)

## Login using other form parameters and url.
## (just an example for setups that do not authenticate through Devilry, this one for UiO.)
#login_url = '{0}/login'.format(devilry_url)
#logincookie = login(login_url, user=username, password=password)

## Load the RESTful API
# Creates proxy classes which makes it natural to program against the RESTful
# interface using python. Exactly what you load here depends on what you want
# to access. See the _Public RESTful API_ section of the API docs at
# http://devilry.org for a complete overview and documentation for all our
# APIs:
#   http://devilry.org/devilry-django/dev/restfulapi/administrator/index.html#restful-apiadministrator
restful_factory = RestfulFactory(devilry_url)
SimplifiedPeriod = restful_factory.make('/administrator/restfulsimplifiedperiod/')
SimplifiedAssignment = restful_factory.make('/administrator/restfulsimplifiedassignment/')
SimplifiedAssignmentGroup = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
SimplifiedExaminer = restful_factory.make('/administrator/restfulsimplifiedexaminer/')


####################################################################
# The actual program
####################################################################

def find_period():
    """ Find the requested period. """
    periodsearch = SimplifiedPeriod.search(logincookie,
                                           filters=[{'field':'short_name', 'comp':'exact', 'value':period_short_name},
                                                    {'field':'parentnode__short_name', 'comp':'exact', 'value':subject_short_name}],
                                           exact_number_of_results=1) # We expect exactly one result, since the combination of period and subject short name is unique. If we should get more that one result, this will throw an exception
    period = periodsearch['items'][0]
    return period

def find_assignments_in_period(period_id):
    """
    Find all assignments within a specific period. Search operates with a
    default limit for the number of results, however since this defaults to 50,
    we should be safe. See find_assignment_groups_in_assignment() below for a
    more robust example.
    """
    assignmentsearch = SimplifiedAssignment.search(logincookie,
                                                   filters=[{'field':'parentnode', 'comp':'exact', 'value':period_id}])
    return assignmentsearch['items']

def find_assignment_groups_in_assignment(assignment_id, limit=10):
    assignment_group_search = SimplifiedAssignmentGroup.search(logincookie,
                                                               limit=limit,
                                                               filters=[{'field':'parentnode', 'comp':'exact', 'value':assignment_id}],
                                                               # Get the latest feedback and students in addition to information stored
                                                               # directly on each group.
                                                               result_fieldgroups=['feedback', 'users'])
    total = assignment_group_search['total']
    if total > limit:
        # Do a new request for _all_ items if the total number of groups is more than the initial limit
        return find_assignment_groups_in_assignment(assignment_id, limit=total)
    else:
        return assignment_group_search['items']



## Examples

def simple_loop_over_all_assignments(period):
    """
    Just loop over the period and print some of the available information about
    each group.
    """
    for assignment in find_assignments_in_period(period['id']):
        print
        print 'Assignment:', assignment['short_name']
        for group in find_assignment_groups_in_assignment(assignment['id']):
            print '-', group['candidates__student__username']
            for attr in ('is_open', 'feedback__points', 'feedback__is_passing_grade', 'feedback__grade'):
                print '   {0}: {1}'.format(attr, group[attr])

def aggregate_points_for_each_student(period):
    """
    Group the information available on a period by student and assignment.
    """
    students = {}
    all_assignments = set()
    for assignment in find_assignments_in_period(period['id']):
        assignment_shortname = assignment['short_name']
        all_assignments.add(assignment_shortname)
        for group in find_assignment_groups_in_assignment(assignment['id']):
            for username in group['candidates__student__username']:
                if not username in students:
                    students[username] = {}
                students[username][assignment_shortname] = group
    return students, all_assignments

def create_table_from_points_aggregate(students, all_assignments):
    """
    Create a table of students and their points on each assignment.
    Takes the output from aggregate_points_for_each_student(...) as arguments.
    """

    # Print header ({0:<20} format string makes positional arg 0 occupy 20 chars left aligned)
    print '{0:<20} '.format('USER'), # Ending comma prevent newline
    for assignment_shortname in all_assignments:
        print '{0:<20} '.format(assignment_shortname),
    print 'SUM'

    # Print points for each user on each assignment
    for student, student_assignments in students.iteritems():
        print '{0:<20}'.format(student),

        total = 0
        for assignment_shortname in all_assignments:
            if assignment_shortname in student_assignments:
                group = student_assignments[assignment_shortname]
                points = group['feedback__points']
                if points == None:
                    points = 'no-feedback'
                else:
                    total += points
            else:
                points = 'no-data' # Student no registered on assignment
            print ' {0:<20}'.format(points),
        print ' {0:<20}'.format(total)


def csv_approvedstats(students, all_assignments):
    """
    Create a csv table of students. For each assignment, a number is added:

        0: no deliveries
        1: Has deliveries Not approved
        2: Approved
    """
    # Print header ({0:<20} format string makes positional arg 0 occupy 20 chars left aligned)
    sys.stdout.write('USER') # Ending comma prevent newline
    for assignment_shortname in all_assignments:
        sys.stdout.write(',{0}'.format(assignment_shortname))
    sys.stdout.write(linesep)

    # Print the documented number for each user on each assignment
    for student, student_assignments in students.iteritems():
        sys.stdout.write(student)

        for assignment_shortname in all_assignments:
            number = 0
            if assignment_shortname in student_assignments:
                group = student_assignments[assignment_shortname]
                deliveries = group['number_of_deliveries']
                if deliveries > 0:
                    if group['feedback__is_passing_grade']:
                        number = 2
                    else:
                        number = 1
            else:
                pass # Student no registered on assignment - keep number at 0
            sys.stdout.write(',{0}'.format(number))
        sys.stdout.write(linesep)


def get_all_examiners_in_period(period):
    """ Get all examiners in the period as a dict where the assignmentgroup is
    the key, and the value is a list of examiners. (for efficient lookup of
    examiner when you have a group). """
    examiners = SimplifiedExaminer.search(logincookie,
                                          limit=100000,
                                          filters=[{'field':'assignmentgroup__parentnode__parentnode',
                                                    'comp':'exact',
                                                    'value':period['id']}],
                                          result_fieldgroups=['userdetails']) # Include username, fullname, ...
    result = {}
    for examiner in examiners['items']:
        groupid = examiner['assignmentgroup']
        if not groupid in result:
            result[groupid] = []
        result[groupid].append(examiner)
    return result

def get_all_assignmentgroups_in_period(period):
    search = SimplifiedAssignmentGroup.search(logincookie,
                                            limit=100000,
                                            filters=[{'field':'parentnode__parentnode',
                                                      'comp':'exact',
                                                      'value':period['id']}],
                                            result_fieldgroups=['assignment']) # Include info about the assignment in the result
    return search['items']

def list_number_of_assignments_corrected_by_examiners(period):
    examiners = get_all_examiners_in_period(period)
    groups = get_all_assignmentgroups_in_period(period)
    assignment_shortnames = ['TOTAL']
    result = {}

    # Count corrected assignments and store them by examiner->assignment->count in ``result``
    for group in get_all_assignmentgroups_in_period(period):
        assignment_shortname = group['parentnode__short_name']
        if not assignment_shortname in assignment_shortnames:
            assignment_shortnames.append(assignment_shortname)
        groupid = group['id']
        if groupid in examiners:
            groupexaminers = examiners[groupid]
            for examiner in groupexaminers:
                examiner_username = examiner['user__username']
                if not examiner_username in result:
                    result[examiner_username] = {'TOTAL': 0}
                result[examiner_username]['TOTAL'] += 1
                if assignment_shortname in result[examiner_username]:
                    result[examiner_username][assignment_shortname] += 1
                else:
                    result[examiner_username][assignment_shortname] = 1
        else:
            pass # Group has no examiners, and perhaps you want to print a warning?

    # Print result in a table
    stringformat = '{:<14} | '
    headerrow = stringformat.format('Examiner')
    for assignment_shortname in assignment_shortnames:
        headerrow += stringformat.format(assignment_shortname)
    print headerrow
    for examiner_username, count_by_assignment in result.iteritems():
        row = stringformat.format(examiner_username)
        for assignment_shortname in assignment_shortnames:
            count = count_by_assignment.get(assignment_shortname, '')
            row += stringformat.format(count)
        print row

try:
    period = find_period()
except HttpResponseBadRequest, e:
    raise SystemExit('ERROR: Could not find requested period: {0}.{1}'.format(subject_short_name, period_short_name))
else:
    print '** Found requested period: {0}.{1}'.format(subject_short_name, period_short_name)

    print
    print "** Loop over all groups in period"
    simple_loop_over_all_assignments(period)

    print
    print "** Period overview"
    create_table_from_points_aggregate(*aggregate_points_for_each_student(period))

    print
    print "** CSV overview (0: no deliveries, 1: Has deliveries, Not approved, 2: Approved"
    csv_approvedstats(*aggregate_points_for_each_student(period))

    print
    print "** Number of groups corrected by each examiner"
    list_number_of_assignments_corrected_by_examiners(period)
