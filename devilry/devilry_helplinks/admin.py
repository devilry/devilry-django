from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import HelpLink


class HelpLinkAdmin(admin.ModelAdmin):
    fieldsets = ((None, {'fields': ('help_url', 'title', 'description')}),
                 (_('Roles that see this link:'),
                  {'fields': ('superuser', 'nodeadmin', 'subjectadmin',
                              'periodadmin', 'assignmentadmin', 'examiner',
                              'student')}))

    list_display = ('title', 'superuser', 'nodeadmin', 'subjectadmin',
                    'periodadmin', 'assignmentadmin', 'examiner', 'student')
    list_filter = ('superuser', 'nodeadmin', 'subjectadmin', 'periodadmin',
                   'assignmentadmin', 'examiner', 'student')

admin.site.register(HelpLink, HelpLinkAdmin)
