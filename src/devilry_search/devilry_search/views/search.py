from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import FieldWithButtons


class SearchForm(forms.Form):
    search = forms.CharField(
        label=_('Search'),
        help_text=_('TODO'),
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

    def form_valid(self, form, context):
        print 'Form:', form