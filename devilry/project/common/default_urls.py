from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponsePermanentRedirect
from devilry.devilry_frontpage.views import frontpage

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
    (r'^markup/', include('devilry.devilry_markup.urls')),
    (r'^authenticate/', include('devilry.devilry_authenticate.urls')),
    url(r'^cradmin_temporaryfileuploadstore/', include('django_cradmin.apps.cradmin_temporaryfileuploadstore.urls')),

    (r'^devilry_help/', include('devilry.devilry_help.urls')),
    (r'^devilry_core/', include('devilry.apps.core.urls')),
    (r'^devilry_usersearch/', include('devilry.devilry_usersearch.urls')),
    (r'^devilry_authenticateduserinfo/', include('devilry.devilry_authenticateduserinfo.urls')),
    (r'^devilry_settings/', include('devilry.devilry_settings.urls')),
    (r'^devilry_helplinks/', include('devilry.devilry_helplinks.urls')),
    ('r^student/assignmentgroup/(?P<assignmentgroupid>\d+)$', redirecto_to_show_delivery),
    (r'^devilry_student/', include('devilry.devilry_student.urls')),
    (r'^devilry_i18n/', include('devilry.devilry_i18n.urls')),
    (r'^superuser/', include(admin.site.urls)),
    (r'^devilry_subjectadmin/', include('devilry.devilry_subjectadmin.urls')),
    (r'^devilry_send_email_to_students/', include('devilry.devilry_send_email_to_students.urls')),
    (r'^devilry_search/', include('devilry.devilry_search.urls')),
    (r'^devilry_header/', include('devilry.devilry_header.urls')),
    ('^devilry_nodeadmin/', include('devilry.devilry_nodeadmin.urls')),
    (r'^devilry_qualifiesforexam/', include('devilry.devilry_qualifiesforexam.urls')),
    (r'^devilry_qualifiesforexam_approved/', include('devilry.devilry_qualifiesforexam_approved.urls')),
    (r'^devilry_qualifiesforexam_points/', include('devilry.devilry_qualifiesforexam_points.urls')),
    (r'^devilry_qualifiesforexam_select/', include('devilry.devilry_qualifiesforexam_select.urls')),
    url(r'^devilry_examiner/', include('devilry.devilry_examiner.urls')),
    url(r'^devilry_gradingsystem/', include('devilry.devilry_gradingsystem.urls')),
    url(r'^devilry_gradingsystemplugin_points/', include('devilry.devilry_gradingsystemplugin_points.urls')),
    url(r'^devilry_gradingsystemplugin_approved/', include('devilry.devilry_gradingsystemplugin_approved.urls')),
    url(r'^devilry_detektor/', include('devilry.devilry_detektor.urls')),
    url(r'^$', frontpage, name='devilry_frontpage'),
)
