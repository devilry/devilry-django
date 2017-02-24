from __future__ import unicode_literals

from django.db import models

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_admin.views.period.manage_tags import bulk_manage_tags
from devilry.apps.core.models import relateduser


class GetQuerySetForRoleMixin(object):
    model = relateduser.RelatedStudent

    def __get_tag_queryset(self):
        return relateduser.RelatedStudentTag.objects\
            .select_related('relatedstudent__user')

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects\
            .filter(period=period)\
            .select_related('user', 'period', 'period__parentnode')\
            .prefetch_related(
                models.Prefetch(
                    'relatedstudenttag_set',
                    queryset=self.__get_tag_queryset()))\
            .order_by('user__shortname')


class GetTagListQuerySetForRoleMixin(object):
    model = relateduser.RelatedStudentTag

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects\
            .get_all_distinct_tags_in_period(period=period)


class StudentSelectMethod(bulk_manage_tags.SelectMethodView):
    def get_context_data(self, **kwargs):
        context_data = super(StudentSelectMethod, self).get_context_data(**kwargs)
        context_data['relateduser_type'] = 'student'
        return context_data


class TagListItemFrame(bulk_manage_tags.TagItemFrame):
    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='manage_tags_students',
            roleid=self.kwargs.get('period').id,
            viewname='remove-tag',
            kwargs={
                'manage_tag': self.kwargs.get('manage_tag'),
                'tag': self.value
            }
        )


class RelatedStudentTagListBuilderView(GetTagListQuerySetForRoleMixin, bulk_manage_tags.BaseTagListbuilderView):
    """
    List distinct tags.
    """
    model = relateduser.RelatedStudentTag
    frame_renderer_class = TagListItemFrame


class RelatedStudentAddTagMultiSelectView(GetQuerySetForRoleMixin, bulk_manage_tags.AddTagMultiSelectView):
    model = relateduser.RelatedStudent

    def get_tag_class(self):
        return relateduser.RelatedStudentTag

    def get_target_renderer_class(self):
        return bulk_manage_tags.SelectItemTagInputTargetRenderer

    def get_form_class(self):
        return bulk_manage_tags.SelectRelatedUsersTagInputForm

    def instantiate_tag_class(self, tag, related_user):
        return relateduser.RelatedStudentTag(tag=tag, relatedstudent=related_user)

    def get_related_user_tag_tags_as_list(self, related_user):
        return [related_student_tags.tag for related_student_tags in related_user.relatedstudenttag_set.all()]

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='students',
            viewname=crapp.INDEXVIEW_NAME,
            roleid=self.request.cradmin_role.id
        )


class RelatedStudentRemoveTagMultiselectView(GetQuerySetForRoleMixin, bulk_manage_tags.RemoveTagMultiSelectView):
    model = relateduser.RelatedStudent

    def get_tag_class(self):
        return relateduser.RelatedStudentTag
    
    def get_queryset_for_role(self, role):
        tag_relateduser_ids = relateduser.RelatedStudentTag.objects\
            .filter(tag=self.tag, prefix='')\
            .values_list('relatedstudent_id', flat=True)
        relateduser_queryset = super(RelatedStudentRemoveTagMultiselectView, self)\
            .get_queryset_for_role(role).filter(id__in=tag_relateduser_ids)
        return relateduser_queryset
    
    def get_tag_queryset_to_delete(self, form):
        return relateduser.RelatedStudentTag.objects\
            .filter(relatedstudent_id__in=self.get_relateduser_ids_list(form))

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='students',
            viewname=crapp.INDEXVIEW_NAME,
            roleid=self.request.cradmin_role.id
        )


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  StudentSelectMethod.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^add-tag$',
                  RelatedStudentAddTagMultiSelectView.as_view(),
                  name='add-tag'),
        crapp.Url(r'^tags/(?P<manage_tag>[\w-]+)$',
                  RelatedStudentTagListBuilderView.as_view(),
                  name='tags-replace'),
        crapp.Url(r'^tags/(?P<manage_tag>[\w-]+)$',
                  RelatedStudentTagListBuilderView.as_view(),
                  name='tags-remove'),
        crapp.Url(r'^tags/(?P<manage_tag>[\w-]+)/(?P<tag>[\w-]+)$',
                  RelatedStudentRemoveTagMultiselectView.as_view(),
                  name='remove-tag')
    ]
