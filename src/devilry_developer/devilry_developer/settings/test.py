from .base import *

# Disable haystack (speeds up tests a lot)
HAYSTACK_SEARCH_ENGINE = 'dummy' # http://django-haystack.readthedocs.org/en/v1.2.7/tutorial.html#modify-your-settings-py
HAYSTACK_SITECONF = 'devilry_developer.dummy_haystack_search_sites'
