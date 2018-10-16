from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponsePermanentRedirect

from devilry.devilry_frontpage import crinstance_frontpage

admin.site.login = login_required(admin.site.login)


def redirecto_to_show_delivery(request, assignmentgroupid):
    delivery_id = request.GET.get('deliveryid')
    if not delivery_id:
        return HttpResponseBadRequest(
            'Requires <code>deliveryid</code> in QUERYSTRING. Perhaps you did not '
            'paste the entire URL from your email?')
    return HttpResponsePermanentRedirect(
        reverse('devilry_student_show_delivery', kwargs={'delivery_id': delivery_id}))


devilry_urls = [
    url(r'^markup/', include('devilry.devilry_markup.urls')),
    url(r'^authenticate/', include('devilry.devilry_authenticate.urls')),
    url(r'^devilry_resetpassword/', include('devilry.devilry_resetpassword.urls')),
    url(r'^cradmin_temporaryfileuploadstore/', include('django_cradmin.apps.cradmin_temporaryfileuploadstore.urls')),

    url(r'^account/', include('devilry.devilry_account.urls')),
    url(r'^devilry_help/', include('devilry.devilry_help.urls')),
    url(r'^devilry_core/', include('devilry.apps.core.urls')),
    url(r'^devilry_settings/', include('devilry.devilry_settings.urls')),
    # url('r^student/assignmentgroup/(?P<assignmentgroupid>\d+)$', redirecto_to_show_delivery),
    url(r'^devilry_student/', include('devilry.devilry_student.urls')),
    url(r'^devilry_group/', include('devilry.devilry_group.urls')),
    url(r'^devilry_gradeform/', include('devilry.devilry_gradeform.urls')),
    url(r'^devilry_admin/', include('devilry.devilry_admin.urls')),
    url(r'^djangoadmin/', admin.site.urls),
    url(r'^devilry_header/', include('devilry.devilry_header.urls')),
    url(r'^devilry_bulkcreate_users/', include('devilry.devilry_bulkcreate_users.urls')),
    url(r'^devilry_examiner/', include('devilry.devilry_examiner.urls')),
    url(r'^devilry_statistics/', include('devilry.devilry_statistics.urls')),
    url(r'^', include(crinstance_frontpage.CrAdminInstance.urls())),
    # url(r'^devilry_qualifiesforexam/', include('devilry.devilry_qualifiesforexam.urls')),
    # url(r'^devilry_qualifiesforexam_approved/', include('devilry.devilry_qualifiesforexam_approved.urls')),
    # url(r'^devilry_qualifiesforexam_points/', include('devilry.devilry_qualifiesforexam_points.urls')),
    # url(r'^devilry_qualifiesforexam_select/', include('devilry.devilry_qualifiesforexam_select.urls')),
    # url(r'^devilry_gradingsystem/', include('devilry.devilry_gradingsystem.urls')),
    # url(r'^devilry_gradingsystemplugin_points/', include('devilry.devilry_gradingsystemplugin_points.urls')),
    # url(r'^devilry_gradingsystemplugin_approved/', include('devilry.devilry_gradingsystemplugin_approved.urls')),
]
