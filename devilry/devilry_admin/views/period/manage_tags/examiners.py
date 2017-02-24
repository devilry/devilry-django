from __future__ import unicode_literals

from django.db import models

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.apps.core.models import relateduser
from devilry.devilry_admin.views.period.manage_tags import bulk_manage_tags


class GetQuerySetForRoleMixin(object):
    model = relateduser.RelatedExaminer

    def __get_tag_queryset(self):
        return relateduser.RelatedExaminerTag.objects\
            .select_related('relatedexaminer__user')

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects\
            .filter(period=period)\
            .select_related('user', 'period', 'period__parentnode')\
            .prefetch_related(
                models.Prefetch(
                    'relatedexaminertag_set',
                    queryset=self.__get_tag_queryset()))\
            .order_by('user__shortname')


class GetTagListQuerySetForRoleMixin(object):
    model = relateduser.RelatedExaminerTag

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects\
            .get_all_distinct_tags_in_period(period=period)


class ExaminerSelectMethod(bulk_manage_tags.SelectMethodView):
    def get_context_data(self, **kwargs):
        context_data = super(ExaminerSelectMethod, self).get_context_data(**kwargs)
        context_data['relateduser_type'] = 'examiner'
        return context_data


class TagListItemFrame(bulk_manage_tags.TagItemFrame):
    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='manage_tags_examiners',
            roleid=self.kwargs.get('period').id,
            viewname='remove-tag',
            kwargs={
                'manage_tag': self.kwargs.get('manage_tag'),
                'tag': self.value
            }
        )


class RelatedExaminerTagListBuilderView(GetTagListQuerySetForRoleMixin, bulk_manage_tags.BaseTagListbuilderView):
    """
    List distinct tags.
    """
    model = relateduser.RelatedExaminerTag
    frame_renderer_class = TagListItemFrame


class RelatedExaminerAddTagMultiSelectView(GetQuerySetForRoleMixin, bulk_manage_tags.AddTagMultiSelectView):
    model = relateduser.RelatedExaminer

    def get_tag_class(self):
        return relateduser.RelatedExaminerTag

    def get_target_renderer_class(self):
        return bulk_manage_tags.SelectItemTagInputTargetRenderer

    def get_form_class(self):
        return bulk_manage_tags.SelectRelatedUsersTagInputForm

    def instantiate_tag_class(self, tag, related_user):
        return relateduser.RelatedExaminerTag(tag=tag, relatedexaminer=related_user)

    def get_related_user_tag_tags_as_list(self, related_user):
        return [related_examiner_tags.tag for related_examiner_tags in related_user.relatedexaminertag_set.all()]

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='examiners',
            viewname=crapp.INDEXVIEW_NAME,
            roleid=self.request.cradmin_role.id
        )


class RelatedExaminerRemoveTagMultiselectView(GetQuerySetForRoleMixin, bulk_manage_tags.RemoveTagMultiSelectView):
    model = relateduser.RelatedExaminer

    def get_tag_class(self):
        return relateduser.RelatedExaminerTag

    def get_queryset_for_role(self, role):
        tag_relateduser_ids = relateduser.RelatedExaminerTag.objects \
            .filter(tag=self.tag, prefix='') \
            .values_list('relatedexaminer_id', flat=True)
        relateduser_queryset = super(RelatedExaminerRemoveTagMultiselectView, self) \
            .get_queryset_for_role(role).filter(id__in=tag_relateduser_ids)
        return relateduser_queryset

    def get_tag_queryset_to_delete(self, form):
        return relateduser.RelatedExaminerTag.objects \
            .filter(relatedexaminer_id__in=self.get_relateduser_ids_list(form))

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='examiners',
            viewname=crapp.INDEXVIEW_NAME,
            roleid=self.request.cradmin_role.id
        )


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  ExaminerSelectMethod.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^add-tag$',
                  RelatedExaminerAddTagMultiSelectView.as_view(),
                  name='add-tag'),
        crapp.Url(r'^tags/(?P<manage_tag>[\w-]+)$',
                  RelatedExaminerTagListBuilderView.as_view(),
                  name='tags-replace'),
        crapp.Url(r'^tags/(?P<manage_tag>[\w-]+)$',
                  RelatedExaminerTagListBuilderView.as_view(),
                  name='tags-remove'),
        crapp.Url(r'^tags/(?P<manage_tag>[\w-]+)/(?P<tag>[\w-]+)$',
                  RelatedExaminerRemoveTagMultiselectView.as_view(),
                  name='remove-tag')

    ]