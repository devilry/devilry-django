from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import cache_page


from .views import admin_assignmentassembly

urlpatterns = patterns(
    'devilry_detektor',
    url(r'^admin/assignmentassembly/(?P<assignmentid>\d+)$',
        # Cache for 5 days - invalidated automatically each
        # time the cheat checking is re-run, so this could
        # in principle be much higher
        cache_page(60 * 60 * 24 * 5)(admin_assignmentassembly.AssignmentAssemblyView.as_view()),
        name='devilry_detektor_admin_assignmentassembly'),
    )
