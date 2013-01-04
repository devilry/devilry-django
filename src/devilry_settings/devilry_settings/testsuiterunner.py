from fnmatch import fnmatchcase
from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings


TEST_FILTER = getattr(settings, 'TEST_FILTER', {'exclude': [], 'include': ['*']})


class FilterableTestSuiteRunner(DjangoTestSuiteRunner):
    def _include(self, path):
        for pattern in TEST_FILTER['exclude']:
            if fnmatchcase(path, pattern):
                return False
        for pattern in TEST_FILTER['include']:
            if fnmatchcase(path, pattern):
                return True
        return False

    def _debug(self, msg):
        if self.verbosity > 2:
            print '[TESTSUITE DEBUG] {0}'.format(msg)

    def build_suite(self, *args, **kwargs):
        suite = super(FilterableTestSuiteRunner, self).build_suite(*args, **kwargs)
        if not args[0]:
            tests = []
            for case in suite:
                path = '{0}.{1}'.format(case.__class__.__module__, case.__class__.__name__)
                if self._include(path):
                    tests.append(case)
                else:
                    self._debug('Ignored {0}'.format(path))
            suite._tests = tests
        return suite