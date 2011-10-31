from devilryrestfullib import (login,
                               RestfulFactory,
                               RestfulError,
                               HttpResponseNotFound,
                               HttpResponseBadRequest,
                               HttpResponseUnauthorized,
                               HttpResponseForbidden,
                               JsonDecodeError)


# may be something like http://devilry.myorganzation.com/some/subpath/ in production
devilry_url = 'http://localhost:8000'

# Log in
# - login url may be somthing else if devilry does not handle the login,
#   however this example assumes that devilry is used for login, and the devilry
#   login form is at /authenticate/login
login_url = '{0}/authenticate/login'.format(devilry_url)
logincookie = login(login_url, username='grandma', password='test')

# Create proxy classes which makes it natural to program against the
# RESTful interface using python.
restful_factory = RestfulFactory(devilry_url)
SimplifiedNode = restful_factory.make("/administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("/administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("/administrator/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("/administrator/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("/administrator/restfulsimplifiedassignmentgroup/")
