try:
    from devilry.project.develop.fabrictasks import *
except ImportError:
    print()
    print()
    print()
    print('*** ERROR: Could not import develop.fabrictasks. You should read ``not_for_deploy/docs/django/gettingstarted.rst``, make sure you are actually in the virtualenv and make sure you have installed all the development requirements.')
    print()
    print()
    print()
    raise
