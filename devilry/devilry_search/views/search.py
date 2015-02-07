from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import FieldWithButtons

from devilry.devilry_search.search_helper import SearchHelper


class SearchForm(forms.Form):
    search = forms.CharField(
        label=_('Search'),
        required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            FieldWithButtons(
                Field('search', autofocus="autofocus"),
                Submit('submit_search', _('Search')))
        )


class SearchView(TemplateView):
    template_name = 'devilry_search/search.django.html'

    def get(self, *args, **kwargs):
        context = kwargs.copy()

        form = SearchForm(self.request.GET)
        if form.is_valid() and form.cleaned_data['search'] != '':
            self.form_valid(form, context)

        context['form'] = form
        return self.render_to_response(context)

    def _prepare_search(self, searchqueryset):
        limit = 100
        return [match for match in searchqueryset[:limit] if match != None]

    def form_valid(self, form, context):
        search_helper = SearchHelper(self.request.user, form.cleaned_data['search'])
        student_results = self._prepare_search(search_helper.get_student_results())
        examiner_results = self._prepare_search(search_helper.get_examiner_results())
        admin_results = self._prepare_search(search_helper.get_admin_results())
        searchcategorycount = len([c for c in (student_results, examiner_results, admin_results) if c])
        try:
            columnsize = 12/searchcategorycount
        except ZeroDivisionError:
            columnsize = 12
        context.update({
            'student_results': student_results,
            'examiner_results': examiner_results,
            'admin_results': admin_results,
            'searchcategorycount': searchcategorycount,
            'columnsize': columnsize
        })
