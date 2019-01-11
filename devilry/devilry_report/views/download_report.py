import io

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views import generic
from django import forms
import django_rq

from devilry.devilry_report.models import DevilryReport
from devilry.devilry_report.rq_task import generate_report


class DownloadReportView(generic.FormView):
    template_name = "devilry_report/download_report.django.html"
    form_class = forms.Form

    # def dispatch(self, request, *args, **kwargs):
    #     try:
    #         self.devilry_report = DevilryReport.objects.get(id=17)
    #     except DevilryReport.DoesNotExist:
    #         self.devilry_report = None
    #
    #     # The request user must be the one that created the report.
    #     # if not self.request.user == self.devilry_report.generated_by_user:
    #     #     raise Http404()
    #     return super(DownloadReportView, self).dispatch(request=request, *args, **kwargs)
    #
    # def post(self, *args, **kwargs):
    #     self.devilry_report = DevilryReport(
    #         generator_type='semesterstudentresults',
    #         generator_options={'test': 'lol'},
    #         generated_by_user=self.request.user)
    #     self.devilry_report.full_clean()
    #     self.devilry_report.save()
    #     django_rq.enqueue(
    #         generate_report,
    #         devilry_report_id=self.devilry_report.id,
    #         period_id=self.request.cradmin_role.id
    #     )
    #     return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('download_report'))
    #
    # def get(self, *args, **kwargs):
    #     if self.devilry_report:
    #         if self.devilry_report.status == DevilryReport.STATUS_CHOICES.SUCCESS.value:
    #             buffer = io.BytesIO()
    #             buffer.write(self.devilry_report.result)
    #             response = HttpResponse(
    #                 buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #             response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(self.devilry_report.output_filename)
    #             response['Content-Length'] = len(buffer.getvalue())
    #             return response
    #     return super(DownloadReportView, self).get(*args, **kwargs)
    #
    # def get_context_data(self, **kwargs):
    #     context = super(DownloadReportView, self).get_context_data(**kwargs)
    #     context['devilry_report'] = self.devilry_report
    #     return context
    #
    # def get_success_url(self):
    #     return HttpResponseRedirect(
    #         self.request.cradmin_app.reverse_appurl('download_report', kwargs={'report_id': self.devilry_report.id})
    #     )
