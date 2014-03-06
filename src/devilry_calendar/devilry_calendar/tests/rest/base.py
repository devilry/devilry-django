from shutil import rmtree
from os import mkdir
from django.test.utils import override_settings
from django.core import management



class HaystackTestSettings(object):
    """
    .. warning:: Rebuilds the search index! Se why below.

    We would like to extends ``override_settings`` context to:

    - set haystack engine to whoosh
    - create the whoosh search index path
    - rebuild the search index on enter
    - remove the search index directory on exit

    But that is not easy, so for now we use the index configured in settings.py directly. See
    the history of this file for our simple tries at solving this problem.
    """
    def __enter__(self):
        management.call_command('rebuild_index', verbosity=0, interactive=False)

    def __exit__(self, *args, **kwargs):
        pass


class AssertSearchResultMixin(object):
    def assert_has_search_result(self, result, **match):
        for item in result:
            allmatched = True
            for key, value in match.iteritems():
                if item.get(key) != value:
                    allmatched = False
                    break
            if allmatched:
                return
        raise AssertionError(
            ('Could not find {match!r} in {result!r}').format(
                match=match,
                result=result
            ))