from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponsePermanentRedirect
from devilry_frontpage.views import frontpage

admin.autodiscover()


def redirecto_to_show_delivery(request, assignmentgroupid):
    delivery_id = request.GET.get('deliveryid')
    if not delivery_id:
        return HttpResponseBadRequest(
            'Requires <code>deliveryid</code> in QUERYSTRING. Perhaps you did not '
            'paste the entire URL from your email?')
    return HttpResponsePermanentRedirect(
        reverse('devilry_student_show_delivery', kwargs={'delivery_id': delivery_id}))


devilry_urls = (
    (r'^markup/', include('devilry.apps.markup.urls')),
    (r'^jsfiledownload/', include('devilry.apps.jsfiledownload.urls')),
    (r'^authenticate/', include('devilry.apps.authenticate.urls')),

    (r'^devilry_usersearch/', include('devilry_usersearch.urls')),
    (r'^devilry_authenticateduserinfo/', include('devilry.devilry_authenticateduserinfo.urls')),
    (r'^devilry_settings/', include('devilry_settings.urls')),
    (r'^devilry_helplinks/', include('devilry_helplinks.urls')),
    ('r^student/assignmentgroup/(?P<assignmentgroupid>\d+)$', redirecto_to_show_delivery),
    (r'^devilry_student/', include('devilry_student.urls')),
    (r'^devilry_i18n/', include('devilry_i18n.urls')),
    (r'^superuser/', include(admin.site.urls)),
    (r'^devilry_subjectadmin/', include('devilry_subjectadmin.urls')),
    (r'^devilry_send_email_to_students/', include('devilry.apps.send_email_to_students.urls')),
    (r'^devilry_search/', include('devilry_search.urls')),
    (r'^devilry_header/', include('devilry_header.urls')),
    ('^devilry_nodeadmin/', include('devilry_nodeadmin.urls')),
    (r'^devilry_qualifiesforexam/', include('devilry_qualifiesforexam.urls')),
    (r'^devilry_qualifiesforexam_approved/', include('devilry_qualifiesforexam_approved.urls')),
    (r'^devilry_qualifiesforexam_points/', include('devilry_qualifiesforexam_points.urls')),
    (r'^devilry_qualifiesforexam_select/', include('devilry_qualifiesforexam_select.urls')),
    url(r'^devilry_examiner/', include('devilry.devilry_examiner.urls')),
    url(r'^devilry_gradingsystem/', include('devilry_gradingsystem.urls')),
    url(r'^devilry_gradingsystemplugin_points/', include('devilry_gradingsystemplugin_points.urls')),
    url(r'^devilry_gradingsystemplugin_approved/', include('devilry_gradingsystemplugin_approved.urls')),
    (r'^devilry_frontpage/', include('devilry_frontpage.urls')),
    url(r'^$', frontpage, name='devilry_frontpage'),
)
