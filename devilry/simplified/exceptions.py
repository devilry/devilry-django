class SimplifiedException(Exception):
    """ Base class for Simplified exceptions. """

class PermissionDenied(SimplifiedException):
    """ Signals that a user tries to access something they are not permitted
    to access. """

class InvalidNumberOfResults(SimplifiedException):
    """ Raised when search() does not return *exactly* the number of results
    specified in the *exact_number_of_results* parameter. """
