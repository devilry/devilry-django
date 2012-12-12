.. _pycharm:

==================================================
PyCharm --- How to setup the IDE with Devilry
==================================================

.. note::
    This guide assumes that you have a working devenv/, where you can use
    ``bin/django_dev.py runserver`` without any errors.


- Open the devilry repository root in PyCharm using ``File->Open directory``.
- When the project has loaded, open the project settings window (``CMD->,`` on Mac).
- Buildout support:
    - Leave disabled - PyCharm does not detect our paths correctly from
      buildout script (does not work with tests), so we add omelette to path
      instead (below).
- Project interpreter:
    - virtualenv at devenv/
    - ``Configure interpreters`` -> ``Select virtualenv devenv/`` -> ``Select paths``:
        - Add ``devenv/parts/omelette/``
- Project structure:
    - Exclude:
        - ``devenv/parts/`` (and ``parts/`` any other ``*env/`` that you may have initialized).
        - ``devenv/static/``
- Django:
    - root:
        devenv/
    - settings module:
        devenv/settings_dev.py
    - manage script (PyCharm selects settings_dev.py wrongly by default)
        devenv/bin/django_dev.py
- JSHint:
    - Assume:
        - Browser
    - Warn:
        - Check all except *When code is in strict mode*.
    - Predefined (you will probably need to add some more when JSHint complains):
        - DevilrySettings,Ext,gettext,ugettext,ngettext,pgettext,interpolate,devilry_subjectadmin
