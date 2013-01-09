from django.utils.translation import ugettext as _
from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from extjs4.views import Extjs4AppView
from cStringIO import StringIO

from devilry.apps.core.models import Period
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment



class AppView(Extjs4AppView):
    template_name = "devilry_subjectadmin/app.django.html"
    appname = 'devilry_subjectadmin'
    #css_staticpath = 'devilry_theme/resources/stylesheets/devilry.css'
    #css_staticpath = 'extjs4/resources/css/ext-all-gray.css'
    title = _('Devilry - Subject administrator')