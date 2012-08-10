###############################
devilry_university_translations
###############################

Overrides some of the Devilry translation strings with terminology that is
better suited for a typical university. Some examples:

- *Department/Faculty/School* instead of *Node*
- *Course* instead of *Subject*
- *Semester* instead of *Period*

This application also serves as a very good example of how to create an
application that overrides certain translation strings.


Installation
============

This application must be added to ``DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS``
and ``INSTALLED_APPS``. Typically looks like this (in ``settings.py``)::

    INSTALLED_APPS += ['devilry_university_translations']
    DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS = ('devilry_university_translations',)

