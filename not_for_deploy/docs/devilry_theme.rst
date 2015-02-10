##################################################
:mod:`devilry.devilry_theme` --- The Devilry theme
##################################################

.. warning::

    The ``devilry.devilry_theme`` app is deprecated. Use ``devilry.devilry_theme2``.


**********
ExtJS apps
**********

ExtJS apps should use the ``extjs4.views.Extjs4AppView`` from `django_extjs4
<https://github.com/espenak/django_extjs4>`_::

    from django.utils.translation import ugettext as _
    from extjs4.views import Extjs4AppView

    class AppView(Extjs4AppView):
        template_name = "devilry_examiner/app.django.html"
        appname = 'devilry_examiner'
        title = _('Myapp') # The initial title until you set one in your app




Writing ExtJS apps is out of scope of this guide. The code above will give you
a view that you can add to your ``urls.py``. You have to put your ``app.js`` in
``static/myapp/app.js``, and it will just work. Take a look at
``devilry_student`` and ``devilry_subjectadmin`` for inspiration.
        


******************
Normal Django apps
******************

Normal Django apps can extend ``devilry_theme/nonapptemplate.django.html``
template. This will give you access to all of the bootstrap CSS, and the
Devilry header at the top of your page. Most parts of the template and its
parent-template can be modified by overriding blocks. See their source code for
more details.


Example:

.. code-block:: django

    {% extends "devilry_theme/nonapptemplate.django.html" %}
    {% load i18n %}
    {% load static %}

    {% block title %}{% trans "Select assignments that students must pass to qualify for final exams" %} - Devilry{% endblock %}

    {% block head-pre %}
        <script type="text/javascript" src="{% static "myapp/stuff.js" %}"></script>
    {% endblock %}

    {% block bodyclass%}devilry_subtlebg{% endblock %}

    {% block bootstrap-body %}
        <div style="margin-top: 40px;">
            
        </div>
    {% endblock %}
