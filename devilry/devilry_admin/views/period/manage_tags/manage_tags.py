from __future__ import unicode_literals

import re

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy
from django.views.generic import TemplateView
from django.views.generic import View
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers import update, delete
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listbuilder import itemvalue

from devilry.apps.core.models import PeriodTag


class PeriodTagForm(forms.Form):
    tag_text = forms.CharField(
        label='Tags',
        widget=forms.Textarea,
        help_text='Add tags here in a comma-separated format, e.g: tag1, tag2, tag3')

    is_hidden = forms.BooleanField(
        label='Hidden',
        initial=False,
        required=False,
        help_text='If you check this, the tag(s) will be marked as hidden.'
    )

    def get_added_tags_list(self):
        """
        Get a list of all the tags added in the form separated by comma.

        Returns:
            (list): List of tags as strings.
        """
        return [tag.strip() for tag in self.cleaned_data['tag_text'].split(',')
                if len(tag) > 0]

    def clean(self):
        super(PeriodTagForm, self).clean()
        if 'tag_text' not in self.cleaned_data or len(self.cleaned_data['tag_text']) == 0:
            raise ValidationError(ugettext_lazy('Tag field is empty.'))
        tag_text = self.cleaned_data['tag_text']
        pattern = '^([^,](,)?)+'
        if not re.match(pattern, tag_text):
            raise ValidationError(
                {'tag_text': ugettext_lazy('Tag text must be in comma separated format! '
                                           'Example: tag1, tag2, tag3')}
            )
        tags_list = [tag_string.strip() for tag_string in tag_text.split(',') if len(tag_string) > 0]
        for tag in tags_list:
            if tags_list.count(tag) > 1:
                raise ValidationError(
                    {'tag_text': ugettext_lazy('"{}" occurs more than once in the form.'.format(tag))}
                )


class TagItemValue(itemvalue.EditDelete):
    template_name = 'devilry_admin/period/manage_tags/tag-item-value.django.html'

    def get_title(self):
        return self.value.displayname


class TagListBuilderListView(listbuilderview.FilterListMixin, listbuilderview.View):
    """
    """
    template_name = 'devilry_admin/period/manage_tags/manage-tags-list-view.django.html'
    model = PeriodTag
    value_renderer_class = TagItemValue

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string}
        )

    def get_unfiltered_queryset_for_role(self, role):
        return self.model.objects.filter(period=role)


class AddTagsView(formbase.FormView):
    """
    View for adding a new tag to the semester.
    """
    template_name = 'devilry_admin/period/manage_tags/add-tag.django.html'
    form_class = PeriodTagForm

    @classmethod
    def deserialize_preview(cls, serialized):
        pass

    def serialize_preview(self, form):
        pass

    def get_field_layout(self):
        return [
            'tag_text',
            'is_hidden'
        ]

    def get_buttons(self):
        return [
            PrimarySubmit('add_tags', ugettext_lazy('Add tags'))
        ]

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='manage_tags',
            roleid=self.request.cradmin_role.id,
            viewname=crapp.INDEXVIEW_NAME
        )

    def get_error_redirect_url(self):
        return self.request.cradmin_app.reverse_appurl(viewname='add_tag')

    def __create_tags(self, tags_string_list, excluded_tags):
        tags = []
        period = self.request.cradmin_role
        for tag_string in tags_string_list:
            if tag_string not in excluded_tags:
                tags.append(PeriodTag(period=period, tag=tag_string))
        with transaction.atomic():
            PeriodTag.objects.bulk_create(tags)
        return len(tags)

    def form_valid(self, form):
        tags_string_list = form.get_added_tags_list()
        excluded_tags = PeriodTag.objects\
            .filter_all_editable_tags_on_period(period=self.request.cradmin_role)\
            .values_list('tag', flat=True)

        # Check if all tags to be added exists.
        if len(tags_string_list) == excluded_tags.count():
            self.add_error_message('The tag(s) you wanted to add already exists.')
            return HttpResponseRedirect(self.get_error_redirect_url())

        # Add success message.
        num_tags_created = self.__create_tags(tags_string_list, excluded_tags)
        message = '{} tag(s) added'
        if excluded_tags.count() > 0:
            message += ', {} tag(s) already existed and were ignored.'
        self.add_success_message(message.format(num_tags_created, excluded_tags.count()))
        return super(AddTagsView, self).form_valid(form=form)

    def add_success_message(self, message):
        messages.success(self.request, message=message)

    def add_error_message(self, message):
        messages.error(self.request, message=message)

    def get_context_data(self, **kwargs):
        context_data = super(AddTagsView, self).get_context_data(**kwargs)
        period = self.request.cradmin_role
        context_data['period'] = period
        context_data['period_tags'] = PeriodTag.objects.get_all_tags_on_period(period=period)
        return context_data


class EditPeriodTagForm(forms.ModelForm):
    """
    """
    class Meta:
        fields = ['tag', 'is_hidden']
        model = PeriodTag


class EditDeleteViewMixin(View):
    """
    """
    model = PeriodTag

    def dispatch(self, request, *args, **kwargs):
        self.tag_id = kwargs.get('pk')
        return super(EditDeleteViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset_for_role(self, role):
        return PeriodTag.objects.filter(period=role, id=self.tag_id)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()


class EditTagView(EditDeleteViewMixin, update.UpdateView):
    form_class = EditPeriodTagForm
    
    def get_form(self, form_class=None):
        form = super(EditTagView, self).get_form(form_class=form_class)
        form.fields['tag'] = forms.CharField(
            label='Tags',
            widget=forms.Textarea,
            help_text='Add tags here in a comma-separated format, e.g: tag1, tag2, tag3')
        form.fields['is_hidden'] = forms.BooleanField(
            label='Hidden',
            initial=False,
            required=False,
            help_text='If you check this, the tag(s) will be marked as hidden.'
        )
        return form
    
    def save_object(self, form, commit=True):
        self.add_success_messages('Tag successfully edited.')
        return super(EditTagView, self).save_object(form=form, commit=True)


class DeleteTagView(EditDeleteViewMixin, delete.DeleteView):
    def get_object_preview(self):
        periodtag = self.model.objects.get(id=self.tag_id)
        return periodtag.tag


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  TagListBuilderListView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  TagListBuilderListView.as_view(),
                  name='filter'),
        crapp.Url(r'^add$',
                  AddTagsView.as_view(),
                  name='add_tag'),
        crapp.Url(r'^edit/(?P<pk>\d+)$',
                  EditTagView.as_view(),
                  name='edit'),
        crapp.Url(r'^delete/(?P<pk>\d+)$',
                  DeleteTagView.as_view(),
                  name='delete')
    ]
