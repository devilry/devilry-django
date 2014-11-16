from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse

from .restful import student_restful
from .views import FileDownloadView
from .views import CompressedFileDownloadView


def redirecto_to_show_delivery(request, assignmentgroupid):
    delivery_id = request.GET.get('deliveryid')
    if not delivery_id:
        return HttpResponseBadRequest('Requires <code>deliveryid</code> in QUERYSTRING. Perhaps you did not paste the entire URL from your email?')
    return HttpResponsePermanentRedirect(reverse('devilry_student_show_delivery',
                                                 kwargs={'delivery_id': delivery_id}))


urlpatterns = patterns('devilry.apps.student',
                       url(r'^assignmentgroup/(?P<assignmentgroupid>\d+)$', redirecto_to_show_delivery),
                       url(r'^show-delivery/filedownload/(?P<filemetaid>\d+)$',
                           login_required(FileDownloadView.as_view()),
                           name='devilry-delivery-file-download'),
                       url(r'^show-delivery/compressedfiledownload/(?P<deliveryid>\d+)$',
                           login_required(CompressedFileDownloadView.as_view()),
                           name='devilry-delivery-download-all-zip')
                       )

urlpatterns += student_restful
