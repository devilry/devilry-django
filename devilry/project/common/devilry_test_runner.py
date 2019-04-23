import warnings

from django.test.runner import DiscoverRunner
#from django.utils.deprecation import RemovedInDjango20Warning


class DevilryTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        # warnings.filterwarnings('ignore', category=RemovedInDjango)
        super(DevilryTestRunner, self).setup_test_environment(**kwargs)
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=ResourceWarning)
