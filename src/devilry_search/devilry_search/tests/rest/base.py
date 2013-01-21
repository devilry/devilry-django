from shutil import rmtree
from os import mkdir
from django.test.utils import override_settings
from django.core import management



class HaystackTestSettings(override_settings):
    """
    Wraps the override_settings context to:
    - set haystack engine to whoosh
    - create the whoosh search index path
    - rebuild the search index on enter
    - remove the search index directory on exit

    ..note::
        We use a directory in CWD for the temporary index because tempfile.mkdtemp does not work.
        Using ``HAYSTACK_WHOOSH_STORAGE='ram' does not work for some reason.
    """
    def __init__(self):
        self.whoosh_path = 'devilry_search_tests_tmp_whooshpath'
        mkdir(self.whoosh_path)
        super(HaystackTestSettings, self).__init__(
            HAYSTACK_SEARCH_ENGINE = 'whoosh',
            HAYSTACK_WHOOSH_PATH = self.whoosh_path
        )

    def __enter__(self):
        super(HaystackTestSettings, self).__enter__()
        management.call_command('rebuild_index', verbosity=0, interactive=False)

    def __exit__(self, *args, **kwargs):
        super(HaystackTestSettings, self).__exit__(*args, **kwargs)
        rmtree(self.whoosh_path)



class AssertSearchResultMixin(object):
    def assert_has_search_result(self, result, modeltype, title, meta=None):
        for item in result:
            if item['type'] == modeltype and item['title'] == title and item['meta'] == meta:
                return
        raise AssertionError(
            ('Could not find {{"type": {modeltype!r}, "title": {title!r}, '
             '"meta": {meta!r}, ...}} in {result!r}').format(
                modeltype=modeltype,
                title=title,
                meta=meta,
                result=result
            ))