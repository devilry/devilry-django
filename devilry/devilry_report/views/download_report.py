import io
import json

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views import generic
from django import forms
import django_rq

from devilry.devilry_report.models import DevilryReport
from devilry.devilry_report.rq_task import generate_report


class ReportForm(forms.Form):
    report_options = forms.CharField(required=True)

    def clean_report_options(self):
        report_options = json.loads(self.cleaned_data['report_options'])
        if 'generator_type' not in report_options:
            raise forms.ValidationError(
                {'report_options': 'Missing \'generator_type\' in report_options'}
            )
        return report_options


class DownloadReportView(generic.FormView):
    template_name = "devilry_report/download_report.django.html"
    form_class = ReportForm

    def __get_devilry_report(self):
        try:
            return DevilryReport.objects.get(id=self.request.GET['report'])
        except DevilryReport.DoesNotExist:
            return None

    def get(self, *args, **kwargs):
        if 'report' not in self.request.GET:
            raise Http404()

        # Fetch report
        self.devilry_report = self.__get_devilry_report()
        if self.devilry_report:
            if self.devilry_report.generated_by_user_id != self.request.user.id:
                # Raise 404 if the requestuser did not create the report.
                raise Http404()
            if self.devilry_report.status == DevilryReport.STATUS_CHOICES.SUCCESS.value:
                # Return a download reponse if the report is finished.
                buffer = io.BytesIO()
                buffer.write(self.devilry_report.result)
                response = HttpResponse(
                    buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename={}'.format(self.devilry_report.output_filename)
                response['Content-Length'] = len(buffer.getvalue())
                return response
        return super(DownloadReportView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DownloadReportView, self).get_context_data(**kwargs)
        context['devilry_report'] = self.devilry_report
        return context

    def form_valid(self, form):
        report_options = form.cleaned_data['report_options']
        self.devilry_report = DevilryReport(
            generator_type=report_options['generator_type'],
            generator_options=report_options['generator_options'],
            generated_by_user=self.request.user
        )
        self.devilry_report.full_clean()
        self.devilry_report.save()
        django_rq.enqueue(
            generate_report,
            devilry_report_id=self.devilry_report.id
        )
        return super(DownloadReportView, self).form_valid(form=form)

    def get_success_url(self):
        return '{}?report={}'.format(
            self.request.cradmin_app.reverse_appurl('download_report'),
            self.devilry_report.id
        )
