import sys
from getpass import getpass
from devilryrestfullib import login, RestfulFactory


####################################################################
# Parse input from user
####################################################################

if len(sys.argv) != 5:
    raise SystemExit("Usage: {0} <devilry-url> <username> <subject-short-name> <period-short-name>".format(sys.argv[0]))

devilry_url = sys.argv[1]
username = sys.argv[2]
subject_short_name = sys.argv[3]
period_short_name = sys.argv[4]
password = getpass()


####################################################################
# Common for more or less any Devilry application
####################################################################

## Log in
# - login url may be somthing else if devilry does not handle the login,
#   however this example assumes that devilry is used for login, and the devilry
#   login form is at /authenticate/login
#login_url = '{0}/authenticate/login'.format(devilry_url)
#logincookie = login(login_url, username=username, password=password)

login_url = '{0}/login'.format(devilry_url)
logincookie = login(login_url, user=username, password=password)

## Load the RESTful API
# Creates proxy classes which makes it natural to program against the RESTful
# interface using python. Exactly what you load here depends on what you want
# to access. See the _Public RESTful API_ section of the API docs at
# http://devilry.org for a complete overview and documentation for all our
# APIs.
restful_factory = RestfulFactory(devilry_url)
SimplifiedPeriod = restful_factory.make("/administrator/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("/administrator/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("/administrator/restfulsimplifiedassignmentgroup/")


####################################################################
# The actual program
####################################################################

# Find a specific period

def find_period():
    periodsearch = SimplifiedPeriod.search(logincookie,
                                           filters=[{'field':"short_name", 'comp':"exact", 'value':period_short_name},
                                                    {'field':"parentnode__short_name", 'comp':"exact", 'value':subject_short_name}],
                                           exact_number_of_results=1) # We expect exactly one result, since the combination of period and subject short name is unique. If we should get more that one result, this will throw an exception
    period = periodsearch['items'][0]
    print '- Found "{short_name} - {long_name}"'.format(**period)
    return period


find_period()
