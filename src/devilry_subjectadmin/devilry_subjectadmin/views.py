from django.views.generic import View
from django.shortcuts import render
from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView



class AppView(Extjs4AppView):
    template_name = "devilry_subjectadmin/app.django.html"
    appname = 'devilry_subjectadmin'
    css_staticpath = 'themebase/resources/stylesheets/devilry.css'
    title = _('Devilry - Subject administrator')
