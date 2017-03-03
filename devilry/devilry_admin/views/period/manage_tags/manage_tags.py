from __future__ import unicode_literals

import re

from django import forms
from django.db import models
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django.views.generic import View

from crispy_forms import layout

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers import update, delete, crudbase
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listbuilder import itemvalue
from django_cradmin.viewhelpers import multiselect2view
from django_cradmin.viewhelpers import multiselect2

from devilry.apps.core.models import PeriodTag
from devilry.apps.core.models import RelatedStudent, RelatedExaminer
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_tags


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
    paginate_by = 10

    def get_pagetitle(self):
        return ugettext_lazy('Tags on {}'.format(self.request.cradmin_role.parentnode))

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_tags.Search())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string}
        )

    def get_unfiltered_queryset_for_role(self, role):
        return self.model.objects.filter(period=role)\
            .prefetch_related(
                models.Prefetch('relatedstudents',
                                queryset=RelatedStudent.objects.filter(period=role)))\
            .prefetch_related(
                models.Prefetch('relatedexaminers',
                            queryset=RelatedExaminer.objects.filter(period=role)))


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
            .filter_editable_tags_on_period(period=self.request.cradmin_role)\
            .filter(tag__in=tags_string_list)\
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
        context_data['period_tags'] = PeriodTag.objects.filter(period=period)
        return context_data


class EditPeriodTagForm(forms.ModelForm):
    """
    """
    class Meta:
        model = PeriodTag
        fields = [
            'tag',
            'is_hidden'
        ]

    def __init__(self, *args, **kwargs):
        self.period = kwargs.pop('period')
        super(EditPeriodTagForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super(EditPeriodTagForm, self).clean()
        tag = cleaned_data['tag']
        if PeriodTag.objects.filter(period=self.period, tag=tag).count() != 0:
            raise ValidationError(ugettext_lazy('{} already exists'.format(tag)))
        return cleaned_data


class EditDeleteViewMixin(View):
    """
    """
    model = PeriodTag

    def dispatch(self, request, *args, **kwargs):
        self.tag_id = kwargs.get('pk')
        self.tag = PeriodTag.objects.get(period=self.request.cradmin_role, id=self.tag_id)
        if self.tag.prefix != '':
            raise Http404()
        return super(EditDeleteViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset_for_role(self, role):
        return PeriodTag.objects.filter(period=role, id=self.tag_id)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()


class EditTagView(crudbase.OnlySaveButtonMixin, EditDeleteViewMixin, update.UpdateView):
    template_name = 'devilry_admin/period/manage_tags/crud.django.html'
    form_class = EditPeriodTagForm

    def get_pagetitle(self):
        return 'Edit {}'.format(PeriodTag.objects.get(id=self.tag_id).displayname)

    def get_form(self, form_class=None):
        form = super(EditTagView, self).get_form(form_class=form_class)
        form.fields['tag'] = forms.CharField(
            label='Tag',
            help_text='Here you can rename the tag.')
        form.fields['is_hidden'] = forms.BooleanField(
            label='Hidden',
            initial=False,
            required=False,
            help_text='If you check this, the tag will be marked as hidden.'
        )
        return form

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('tag', focusonme='focusonme'),
                layout.Field('is_hidden'),
                css_class='cradmin-globalfields'
            )
        ]

    def save_object(self, form, commit=True):
        period_tag = super(EditTagView, self).save_object(form=form, commit=False)
        period_tag.modified_datetime = timezone.now()
        self.add_success_messages('Tag successfully edited.')
        return super(EditTagView, self).save_object(form=form, commit=True)

    def get_form_kwargs(self):
        kwargs = super(EditTagView, self).get_form_kwargs()
        kwargs['period'] = self.request.cradmin_role
        return kwargs


class DeleteTagView(EditDeleteViewMixin, delete.DeleteView):
    template_name = 'devilry_admin/period/manage_tags/delete.django.html'

    def get_object_preview(self):
        periodtag = self.model.objects.get(id=self.tag_id)
        return periodtag.tag


class SelectedRelatedUsersForm(forms.Form):
    invalid_item_selected_message = 'Invalid relateduser was selected'
    selected_items = forms.ModelMultipleChoiceField(
        queryset=None,
        error_messages={
            'invalid_choice': invalid_item_selected_message
        }
    )

    def __init__(self, *args, **kwargs):
        relatedusers_queryset = kwargs.pop('relatedusers_queryset')
        super(SelectedRelatedUsersForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = relatedusers_queryset


class SelectableItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    """
    Selectable item.
    """
    valuealias = 'relateduser'

    def get_title(self):
        return self.relateduser.user.shortname


class SelectedItemTargetRenderer(multiselect2.target_renderer.Target):
    def get_with_items_title(self):
        return pgettext_lazy('admin multiselect2_relateduser',
                             'Selected users')

    def get_without_items_text(self):
        return pgettext_lazy('admin multiselect2_relateduser',
                             'No related users selected')


class BaseRelatedUserMultiSelectView(multiselect2view.ListbuilderView):
    """
    Base multiselect view for :class:`~.devilry.apps.core.models.relateduser.RelatedExaminer`s and
    :class:`~.devilry.apps.core.models.relateduser.RelatedStudents`s.

    Attributes:
        tag_name(str): the specific tag of a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    template_name = 'devilry_admin/period/manage_tags/base-multiselect-view.django.html'
    value_renderer_class = SelectableItemValue
    form_class = SelectedRelatedUsersForm
    tag_name = None
    relateduser_string = ''

    def dispatch(self, request, *args, **kwargs):
        self.tag_name = kwargs.get('tag')
        return super(BaseRelatedUserMultiSelectView, self).dispatch(request, *args, **kwargs)

    def get_target_renderer_class(self):
        return SelectedItemTargetRenderer

    def get_period_tag(self):
        period = self.request.cradmin_role
        return PeriodTag.objects.get(period=period, tag=self.tag_name)

    def get_queryset_for_role(self, role):
        """
        Get all relatedstudents for the period that are not already registered on the
        tag provided with the url.
        """
        return self.model.objects.filter(period=role)

    def get_form_kwargs(self):
        period = self.request.cradmin_role
        kwargs = super(BaseRelatedUserMultiSelectView, self).get_form_kwargs()
        kwargs['relatedusers_queryset'] = self.get_queryset_for_role(role=period)
        return kwargs

    def add_success_message(self, message):
        messages.success(self.request, message=message)

    def add_error_message(self, message):
        messages.error(self.request, message=message)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()


class AddRelatedUserToTagMultiSelectView(BaseRelatedUserMultiSelectView):
    """
    Add related users to a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    def get_queryset_for_role(self, role):
        return super(AddRelatedUserToTagMultiSelectView, self)\
            .get_queryset_for_role(role=role)\
            .exclude(periodtag__tag=self.tag_name)

    def add_related_users(self, period_tag, related_users):
        with transaction.atomic():
            for related_user in related_users:
                related_user.periodtag_set.add(period_tag)

    def form_valid(self, form):
        period_tag = self.get_period_tag()
        related_users = form.cleaned_data['selected_items']
        self.add_related_users(period_tag=period_tag, related_users=related_users)
        self.add_success_message(message='{} {} successfully added'.format(len(related_users), self.relateduser_string))
        return super(AddRelatedUserToTagMultiSelectView, self).form_valid(form=form)
    

class RemoveRelatedUserFromTagMultiSelectView(BaseRelatedUserMultiSelectView):
    """
    Remove related users from a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    def get_queryset_for_role(self, role):
        return super(RemoveRelatedUserFromTagMultiSelectView, self)\
            .get_queryset_for_role(role=role)\
            .filter(periodtag__tag=self.tag_name)

    def remove_related_users(self, period_tag, related_users):
        with transaction.atomic():
            for related_user in related_users:
                related_user.periodtag_set.remove(period_tag)

    def form_valid(self, form):
        period_tag = self.get_period_tag()
        related_users = form.cleaned_data['selected_items']
        self.remove_related_users(period_tag=period_tag, related_users=related_users)
        self.add_success_message(
            message='{} {} successfully removed'.format(len(related_users), self.relateduser_string))
        return super(RemoveRelatedUserFromTagMultiSelectView, self).form_valid(form=form)


class RelatedExaminerAddView(AddRelatedUserToTagMultiSelectView):
    """
    Multi-select add view for :class:`~.devilry.apps.core.models.relateduser.RelatedExaminer`.
    """
    model = RelatedExaminer
    relateduser_string = 'examiner(s)'

    def get_pagetitle(self):
        return ugettext_lazy('Add examiners to tag {}'.format(self.tag_name))


class RelatedExaminerRemoveView(RemoveRelatedUserFromTagMultiSelectView):
    """
    Multi-select remove view for :class:`~.devilry.apps.core.models.relateduser.RelatedExaminer`.
    """
    model = RelatedExaminer
    relateduser_string = 'examiner(s)'

    def get_pagetitle(self):
        return ugettext_lazy('Remove examiners from tag {}'.format(self.tag_name))


class RelatedStudentAddView(AddRelatedUserToTagMultiSelectView):
    """
    Multi-select add view for :class:`~.devilry.apps.core.models.relateduser.RelatedStudent`.
    """
    model = RelatedStudent
    relateduser_string = 'student(s)'

    def get_pagetitle(self):
        return ugettext_lazy('Add students to tag {}'.format(self.tag_name))


class RelatedStudentRemoveView(RemoveRelatedUserFromTagMultiSelectView):
    """
    Multi-select remove view for :class:`~.devilry.apps.core.models.relateduser.RelatedStudent`.
    """
    model = RelatedStudent
    relateduser_string = 'student(s)'

    def get_pagetitle(self):
        return ugettext_lazy('Remove students from tag {}'.format(self.tag_name))


class App(crapp.App):

    @classmethod
    def get_related_examiner_add_view(cls):
        return RelatedExaminerAddView

    @classmethod
    def get_related_examiner_remove_view(cls):
        return RelatedExaminerRemoveView

    @classmethod
    def get_related_student_add_view(cls):
        return RelatedStudentAddView

    @classmethod
    def get_related_student_remove_view(cls):
        return RelatedStudentRemoveView

    @classmethod
    def get_appurls(cls):
        return [
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
                      name='delete'),
            crapp.Url('^add-examiners/(?P<tag>[\w-]+)$',
                      cls.get_related_examiner_add_view().as_view(),
                      name='add_examiners'),
            crapp.Url('^remove-examiners/(?P<tag>[\w-]+)$',
                      cls.get_related_examiner_remove_view().as_view(),
                      name='remove_examiners'),
            crapp.Url('^add-students/(?P<tag>[\w-]+)$',
                      cls.get_related_student_add_view().as_view(),
                      name='add_students'),
            crapp.Url('^remove-students/(?P<tag>[\w-]+)$',
                      cls.get_related_student_remove_view().as_view(),
                      name='remove_students')
        ]