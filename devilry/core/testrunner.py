from django.test.simple import DjangoTestSuiteRunner
import coverage


class CoverageTestRunner(DjangoTestSuiteRunner):
    """ Testrunner with wrapped by coverage.py
    (http://nedbatchelder.com/code/coverage/). """
    def run_suite(self, *args, **kwargs):
        cov = coverage.coverage()
        cov.start()
        r = super(CoverageTestRunner, self).run_suite(*args, **kwargs)
        cov.stop()
        cov.save()

        return r
