# -*- coding: utf-8 -*-


import re

from django import forms
from django.db import models
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy, pgettext_lazy
from django.views.generic import TemplateView
from django.views.generic import View

from crispy_forms import layout

from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.crispylayouts import PrimarySubmit
from cradmin_legacy.viewhelpers import formbase
from cradmin_legacy.viewhelpers import update, delete, crudbase
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers.listbuilder import itemvalue
from cradmin_legacy.viewhelpers import multiselect2view
from cradmin_legacy.viewhelpers import multiselect2

from devilry.apps.core.models import PeriodTag
from devilry.apps.core.models import RelatedStudent, RelatedExaminer
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_tags, listfilter_relateduser


class TagItemValue(itemvalue.EditDelete):
    template_name = 'devilry_admin/period/manage_tags/tag-item-value.django.html'

    def get_title(self):
        return self.value.displayname


class HideShowPeriodTag(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        tag_id = self.__get_tag_id(request)
        period_tag = self.__get_period_tag(tag_id)
        hide = False
        if not period_tag.is_hidden:
            hide = True
        period_tag.is_hidden = hide
        period_tag.full_clean()
        period_tag.save()
        return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appindexurl()))

    def __get_tag_id(self, request):
        tag_id = request.GET.get('tag_id', None)
        if not tag_id:
            raise Http404('Missing parameters.')
        return tag_id

    def __get_period_tag(self, tag_id):
        try:
            period_tag = PeriodTag.objects.get(id=tag_id)
        except PeriodTag.DoesNotExist:
            raise Http404('Tag does not exist.')
        return period_tag


class TagListBuilderListView(listbuilderview.FilterListMixin, listbuilderview.View):
    """
    """
    template_name = 'devilry_admin/period/manage_tags/manage-tags-list-view.django.html'
    model = PeriodTag
    value_renderer_class = TagItemValue
    paginate_by = 10

    def get_pagetitle(self):
        return gettext_lazy('Tags on %(what)s') % {'what': self.request.cradmin_role.parentnode}

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_tags.Search())
        # filterlist.append(listfilter_tags.IsHiddenFilter())
        filterlist.append(listfilter_tags.IsHiddenRadioFilter())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string}
        )

    def get_unfiltered_queryset_for_role(self, role):
        queryset = self.model.objects.filter(period=role)\
            .prefetch_related(
                models.Prefetch('relatedstudents',
                                queryset=RelatedStudent.objects.all().select_related('user')
                                .order_by('user__shortname')))\
            .prefetch_related(
                models.Prefetch('relatedexaminers',
                                queryset=RelatedExaminer.objects.all().select_related('user')
                                .order_by('user__shortname')))
        return queryset

    def get_no_items_message(self):
        return pgettext_lazy(
            'TagListBuilderListView get_no_items_message',
            'No period tags'
        )


class CreatePeriodTagForm(forms.Form):
    tag_text = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(CreatePeriodTagForm, self).__init__(*args, **kwargs)
        self.fields['tag_text'].label = gettext_lazy('Tags')
        self.fields['tag_text'].help_text = gettext_lazy(
            'Enter tags here. Tags must be in a comma separated format, '
            'e.g: tag1, tag2, tag3. '
            'Each tag may be up to 15 characters long.'
        )
        self.fields['tag_text'].widget = forms.Textarea()

    def get_added_tags_list(self):
        """
        Get a list of all the tags added in the form separated by comma.

        Returns:
            (list): List of tags as strings.
        """
        return [tag.strip() for tag in self.cleaned_data['tag_text'].split(',')
                if len(tag.strip()) > 0]

    def clean(self):
        super(CreatePeriodTagForm, self).clean()
        if 'tag_text' not in self.cleaned_data or len(self.cleaned_data['tag_text']) == 0:
            raise ValidationError(gettext_lazy('Tag field is empty.'))
        tags_list = self.get_added_tags_list()
        if len(tags_list) == 0:
            if len(tags_list) > 15:
                raise ValidationError(
                    {'tag_text': gettext_lazy('Wrong format. Example: tag1, tag2, tag3')}
                )
        for tag in tags_list:
            if len(tag) > 15:
                raise ValidationError(
                    {'tag_text': gettext_lazy('One or more tags exceed the limit of 15 characters.')}
                )
            if tags_list.count(tag) > 1:
                raise ValidationError(
                    {'tag_text': gettext_lazy('"%(what)s" occurs more than once in the form.') % {'what': tag}}
                )


class AddTagsView(formbase.FormView):
    """
    View for adding a new tag to the semester.
    """
    template_name = 'devilry_admin/period/manage_tags/add-tag.django.html'
    form_class = CreatePeriodTagForm

    @classmethod
    def deserialize_preview(cls, serialized):
        pass

    def serialize_preview(self, form):
        pass

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('tag_text', focusonme='focusonme'),
                css_class='cradmin-globalfields'
            )
        ]

    def get_buttons(self):
        return [
            PrimarySubmit('add_tags', gettext_lazy('Add tags'))
        ]

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='manage_tags',
            roleid=self.request.cradmin_role.id,
            viewname=crapp.INDEXVIEW_NAME
        )

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
            self.add_error_message(gettext_lazy('The tag(s) you wanted to add already exists.'))
            return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appurl(viewname='add_tag')))

        # Add success message.
        num_tags_created = self.__create_tags(tags_string_list, excluded_tags)
        message = gettext_lazy('%(created)d tag(s) added') % {'created': num_tags_created}
        if excluded_tags.count() > 0:
            message += gettext_lazy(
                ', %(excluded)d tag(s) already existed and were ignored.') % {
                'excluded': excluded_tags.count()
            }
        self.add_success_message(message)
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
    Form for editing :class:`~.devilry.apps.core.models.period_tag.PeriodTag`s.
    """
    class Meta:
        model = PeriodTag
        fields = [
            'tag',
        ]

    def __init__(self, *args, **kwargs):
        self.period = kwargs.pop('period')
        self.tagobject = kwargs.pop('tagobject')
        super(EditPeriodTagForm, self).__init__(*args, **kwargs)
        self.fields['tag'].label = gettext_lazy('Tag name')
        self.fields['tag'].help_text = gettext_lazy(
            'Rename the tag here. Up to 15 characters. '
            'Can contain any character except comma(,)'
        )
    
    def clean(self):
        cleaned_data = super(EditPeriodTagForm, self).clean()
        if 'tag' not in self.cleaned_data or len(self.cleaned_data['tag']) == 0:
            raise ValidationError(
                {'tag': gettext_lazy('Tag cannot be empty.')}
            )
        tag = cleaned_data['tag']
        if PeriodTag.objects.filter(period=self.period, tag=tag).exists():
            if tag != self.tagobject.tag:
                raise ValidationError(gettext_lazy('%(what)s already exists') % {'what': tag})
        if ',' in tag:
            raise ValidationError(
                {'tag': gettext_lazy('Tag contains a comma(,).')}
            )
        return cleaned_data


class EditDeleteViewMixin(View):
    """
    Edit/delete mixin for :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.

    Raises:
        Http404: if prefix :attr:`~.devilry.apps.core.models.period_tag.PeriodTag.prefix`
            is not blank.
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
        return str(self.request.cradmin_app.reverse_appindexurl())


class EditTagView(crudbase.OnlySaveButtonMixin, EditDeleteViewMixin, update.UpdateView):
    """
    Edit a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    template_name = 'devilry_admin/period/manage_tags/crud.django.html'
    form_class = EditPeriodTagForm

    def get_pagetitle(self):
        return gettext_lazy('Edit %(what)s') % {
            'what': self.tag.displayname
        }

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('tag', focusonme='focusonme'),
                css_class='cradmin-globalfields'
            )
        ]

    def save_object(self, form, commit=True):
        period_tag = super(EditTagView, self).save_object(form=form, commit=False)
        period_tag.modified_datetime = timezone.now()
        self.add_success_messages(gettext_lazy('Tag successfully edited.'))
        return super(EditTagView, self).save_object(form=form, commit=True)

    def get_form_kwargs(self):
        kwargs = super(EditTagView, self).get_form_kwargs()
        kwargs['period'] = self.request.cradmin_role
        kwargs['tagobject'] = self.tag
        return kwargs

    def get_context_data(self, **kwargs):
        period = self.request.cradmin_role
        context_data = super(EditTagView, self).get_context_data(**kwargs)
        context_data['period'] = period
        context_data['period_tags'] = PeriodTag.objects\
            .filter_editable_tags_on_period(period=period)
        return context_data


class DeleteTagView(EditDeleteViewMixin, delete.DeleteView):
    """
    Delete a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    template_name = 'devilry_admin/period/manage_tags/delete.django.html'

    def get_object_preview(self):
        periodtag = self.model.objects.get(id=self.tag_id)
        return periodtag.tag


class SelectedRelatedUsersForm(forms.Form):
    invalid_item_selected_message = gettext_lazy(
        'Invalid user was selected. This may happen if someone else added or '
        'removed one or more of the available users while you were selecting. '
        'Please try again.'
    )
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


class SelectedItemsTarget(multiselect2.target_renderer.Target):
    def __init__(self, *args, **kwargs):
        self.relateduser_type = kwargs.pop('relateduser_type')
        super(SelectedItemsTarget, self).__init__(*args, **kwargs)

    def get_with_items_title(self):
        return pgettext_lazy('admin multiselect2_relateduser',
                             'Selected %(what)s') % {'what': self.relateduser_type}

    def get_without_items_text(self):
        return pgettext_lazy('admin multiselect2_relateduser',
                             'No %(what)s selected') % {'what': self.relateduser_type}


class SelectedRelatedUserItem(multiselect2.selected_item_renderer.SelectedItem):
    valuealias = 'relateduser'

    def get_title(self):
        return self.relateduser.user.shortname


class SelectableRelatedUserItem(multiselect2.listbuilder_itemvalues.ItemValue):
    valuealias = 'relateduser'
    selected_item_renderer_class = SelectedRelatedUserItem

    def get_title(self):
        return self.relateduser.user.shortname


class BaseRelatedUserMultiSelectView(multiselect2view.ListbuilderFilterView):
    """
    Base multiselect view for :class:`~.devilry.apps.core.models.relateduser.RelatedExaminer`s and
    :class:`~.devilry.apps.core.models.relateduser.RelatedStudents`s.
    """
    template_name = 'devilry_admin/period/manage_tags/base-multiselect-view.django.html'
    value_renderer_class = SelectableRelatedUserItem
    form_class = SelectedRelatedUsersForm
    paginate_by = 20

    #: the specific tag :attr:`~.devilry.apps.core.models.period_tag.PeriodTag.tag`.
    tag_id = None

    #: Type of related user as shown in ui.
    #: e.g 'student' or 'examiner'
    relateduser_string = ''

    def dispatch(self, request, *args, **kwargs):
        self.tag_id = kwargs.get('tag_id')
        return super(BaseRelatedUserMultiSelectView, self).dispatch(request, *args, **kwargs)

    def get_target_renderer_class(self):
        return SelectedItemsTarget

    def get_period_tag(self):
        return PeriodTag.objects.get(id=self.tag_id)

    def get_tags_for_period(self):
        return PeriodTag.objects.filter(period=self.request.cradmin_role)

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())
        filterlist.append(listfilter_relateduser.TagSelectFilter(period=self.request.cradmin_role))

    def get_unfiltered_queryset_for_role(self, role):
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
    
    def get_target_renderer_kwargs(self):
        kwargs = super(BaseRelatedUserMultiSelectView, self).get_target_renderer_kwargs()
        kwargs['relateduser_type'] = self.relateduser_string
        return kwargs
    
    def add_success_message(self, message):
        messages.success(self.request, message=message)

    def add_error_message(self, message):
        messages.error(self.request, message=message)

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appindexurl())


class AddRelatedUserToTagMultiSelectView(BaseRelatedUserMultiSelectView):
    """
    Add related users to a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    def get_pagetitle(self):
        tag_displayname = self.get_period_tag().displayname
        return gettext_lazy(
            'Add %(user)s to %(tag)s') % {
            'user': self.relateduser_string,
            'tag': tag_displayname
        }

    def get_queryset_for_role(self, role):
        return super(AddRelatedUserToTagMultiSelectView, self)\
            .get_queryset_for_role(role=role)\
            .exclude(periodtag__id=self.tag_id)

    def add_related_users(self, period_tag, related_users):
        with transaction.atomic():
            for related_user in related_users:
                related_user.periodtag_set.add(period_tag)

    def form_valid(self, form):
        period_tag = self.get_period_tag()
        related_users = form.cleaned_data['selected_items']
        self.add_related_users(period_tag=period_tag, related_users=related_users)
        self.add_success_message(
            message=gettext_lazy(
                '%(number_users)d %(user_string)s added successfully.'
            ) % {
                'number_users': len(related_users),
                'user_string': self.relateduser_string,
            }
        )

        return super(AddRelatedUserToTagMultiSelectView, self).form_valid(form=form)


class RemoveRelatedUserFromTagMultiSelectView(BaseRelatedUserMultiSelectView):
    """
    Remove related users from a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
    """
    def get_pagetitle(self):
        tag_displayname = self.get_period_tag().displayname
        return gettext_lazy(
            'Remove %(user)s from %(tag)s'
        ) % {
            'user': self.relateduser_string,
            'tag': tag_displayname
        }

    def get_queryset_for_role(self, role):
        return super(RemoveRelatedUserFromTagMultiSelectView, self)\
            .get_queryset_for_role(role=role)\
            .filter(periodtag__id=self.tag_id)

    def remove_related_users(self, period_tag, related_users):
        with transaction.atomic():
            for related_user in related_users:
                related_user.periodtag_set.remove(period_tag)

    def form_valid(self, form):
        period_tag = self.get_period_tag()
        related_users = form.cleaned_data['selected_items']
        self.remove_related_users(period_tag=period_tag, related_users=related_users)
        self.add_success_message(
            message=gettext_lazy(
                '%(number_users)d %(user_string)s removed successfully'
            ) % {
                'number_users': len(related_users),
                'user_string': self.relateduser_string
            }
        )
        return super(RemoveRelatedUserFromTagMultiSelectView, self).form_valid(form=form)


class SelectedRelatedExaminerForm(SelectedRelatedUsersForm):
    invalid_item_selected_message = gettext_lazy('Invalid examiner was selected.')


class SelectedRelatedStudentForm(SelectedRelatedUsersForm):
    invalid_item_selected_message = gettext_lazy('Invalid student was selected.')


class ExaminerMultiSelectViewMixin(object):
    model = RelatedExaminer
    relateduser_string = gettext_lazy('examiner')
    form_class = SelectedRelatedExaminerForm


class StudentMultiSelectViewMixin(object):
    model = RelatedStudent
    relateduser_string = gettext_lazy('student')
    form_class = SelectedRelatedStudentForm


class RelatedExaminerAddView(ExaminerMultiSelectViewMixin, AddRelatedUserToTagMultiSelectView):
    """
    Multi-select add view for :class:`~.devilry.apps.core.models.relateduser.RelatedExaminer`.
    """
    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'add_examiners_filter', kwargs={
                'tag_id': self.tag_id,
                'filters_string': filters_string
            })


class RelatedExaminerRemoveView(ExaminerMultiSelectViewMixin, RemoveRelatedUserFromTagMultiSelectView):
    """
    Multi-select remove view for :class:`~.devilry.apps.core.models.relateduser.RelatedExaminer`.
    """
    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'remove_examiners_filter', kwargs={
                'tag_id': self.tag_id,
                'filters_string': filters_string
            })


class RelatedStudentAddView(StudentMultiSelectViewMixin, AddRelatedUserToTagMultiSelectView):
    """
    Multi-select add view for :class:`~.devilry.apps.core.models.relateduser.RelatedStudent`.
    """
    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'add_students_filter', kwargs={
                'tag_id': self.tag_id,
                'filters_string': filters_string
            })


class RelatedStudentRemoveView(StudentMultiSelectViewMixin, RemoveRelatedUserFromTagMultiSelectView):
    """
    Multi-select remove view for :class:`~.devilry.apps.core.models.relateduser.RelatedStudent`.
    """
    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'remove_students_filter', kwargs={
                'tag_id': self.tag_id,
                'filters_string': filters_string
            })


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
                  name='delete'),
        crapp.Url(r'^toggle-visibility$',
                  HideShowPeriodTag.as_view(),
                  name='toggle_visibility'),

        crapp.Url('^add-examiners/(?P<tag_id>\d+)$',
                  RelatedExaminerAddView.as_view(),
                  name='add_examiners'),
        crapp.Url('^add-examiners/(?P<tag_id>\d+)/(?P<filters_string>.+)?$',
                  RelatedExaminerAddView.as_view(),
                  name='add_examiners_filter'),
        crapp.Url('^remove-examiners/(?P<tag_id>\d+)$',
                  RelatedExaminerRemoveView.as_view(),
                  name='remove_examiners'),
        crapp.Url('^remove-examiners/(?P<tag_id>\d+)/(?P<filters_string>.+)?$',
                  RelatedExaminerRemoveView.as_view(),
                  name='remove_examiners_filter'),

        crapp.Url('^add-students/(?P<tag_id>\d+)$',
                  RelatedStudentAddView.as_view(),
                  name='add_students'),
        crapp.Url('^add-students/(?P<tag_id>\d+)/(?P<filters_string>.+)?$',
                  RelatedStudentAddView.as_view(),
                  name='add_students_filter'),
        crapp.Url('^remove-students/(?P<tag_id>\d+)$',
                  RelatedStudentRemoveView.as_view(),
                  name='remove_students'),
        crapp.Url('^remove-students/(?P<tag_id>\d+)/(?P<filters_string>.+)?$',
                  RelatedStudentRemoveView.as_view(),
                  name='remove_students_filter'),
    ]
