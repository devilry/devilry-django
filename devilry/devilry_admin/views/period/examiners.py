from cradmin_legacy import crapp
from cradmin_legacy.crispylayouts import DangerSubmit
from cradmin_legacy.viewhelpers.listbuilder.itemframe import DefaultSpacingItemFrame
from cradmin_legacy.viewhelpers.listbuilder.lists import RowList
from django.contrib import messages
from django.http import Http404
from django.utils.translation import gettext_lazy

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_account.models import PermissionGroup, User
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedexaminer
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser
from devilry.devilry_admin.views.common import bulkimport_users_common
from devilry.devilry_cradmin import devilry_multiselect2
from devilry.devilry_cradmin.devilry_listfilter.utils import WithResultValueRenderable
from devilry.devilry_cradmin.viewhelpers import devilry_confirmview


class GetQuerysetForRoleMixin(object):
    model = RelatedExaminer

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects.filter(period=period).order_by("user__shortname")


class OverviewItemValue(listbuilder_relatedexaminer.OnPeriodItemValue):
    template_name = "devilry_admin/period/examiners/overview-itemvalue.django.html"


class ExaminerUserListMatchResultRenderable(WithResultValueRenderable):
    def get_object_name_singular(self, num_matches):
        return gettext_lazy("examiner")

    def get_object_name_plural(self, num_matches):
        return gettext_lazy("examiners")


class RowListWithMatchResults(RowList):
    def append_results_renderable(self):
        result_info_renderable = ExaminerUserListMatchResultRenderable(
            value=None, num_matches=self.num_matches, num_total=self.num_total
        )
        self.renderable_list.insert(0, DefaultSpacingItemFrame(inneritem=result_info_renderable))

    def __init__(self, num_matches, num_total, page):
        self.num_matches = num_matches
        self.num_total = num_total
        self.page = page
        super().__init__()

        if page == 1:
            self.append_results_renderable()


class Overview(listbuilder_relatedexaminer.VerticalFilterListView):
    listbuilder_class = RowListWithMatchResults
    value_renderer_class = OverviewItemValue
    template_name = "devilry_admin/period/examiners/overview.django.html"

    def get_period(self):
        return self.request.cradmin_role

    def add_filterlist_items(self, filterlist):
        super(Overview, self).add_filterlist_items(filterlist=filterlist)
        filterlist.append(listfilter_relateduser.IsActiveFilter())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("filter", kwargs={"filters_string": filters_string})

    def get_listbuilder_list_kwargs(self):
        kwargs = super().get_listbuilder_list_kwargs()
        kwargs["num_matches"] = self.num_matches or 0
        kwargs["num_total"] = self.num_total or 0
        kwargs["page"] = self.request.GET.get("page", 1)
        return kwargs

    def get_queryset_for_role(self, role):
        queryset = super().get_queryset_for_role(role=role)

        # Set filtered count on self.
        self.num_matches = queryset.count()
        return queryset

    def get_unfiltered_queryset_for_role(self, role):
        period = role
        queryset = self.model.objects.filter(period=period).select_related("user")
        self.num_total = queryset.count()
        return queryset

    def __user_is_department_admin(self):
        requestuser_devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        return requestuser_devilryrole == PermissionGroup.GROUPTYPE_DEPARTMENTADMIN

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context["period"] = self.request.cradmin_role
        context["user_is_department_admin"] = self.__user_is_department_admin()
        return context


class SingleRelatedExaminerMixin(GetQuerysetForRoleMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.relatedexaminer = (
                self.get_queryset_for_role(role=self.request.cradmin_role).select_related("user").get(id=kwargs["pk"])
            )
        except RelatedExaminer.DoesNotExist:
            raise Http404()
        return super(SingleRelatedExaminerMixin, self).dispatch(request, *args, **kwargs)


class DeactivateView(SingleRelatedExaminerMixin, devilry_confirmview.View):
    """
    View used to deactivate examiners from a period.
    """

    def get_pagetitle(self):
        return gettext_lazy("Deactivate examiner: %(user)s?") % {
            "user": self.relatedexaminer.user.get_full_name(),
        }

    def get_confirm_message(self):
        period = self.request.cradmin_role
        return gettext_lazy(
            "Are you sure you want to make %(user)s "
            "an inactive examiner for %(period)s? Inactive examiners "
            "can not access any assignments within the semester. "
            "You can re-activate a deactivated examiner at any time."
        ) % {
            "user": self.relatedexaminer.user.get_full_name(),
            "period": period.get_path(),
        }

    def get_submit_button_label(self):
        return gettext_lazy("Deactivate")

    def get_submit_button_class(self):
        return DangerSubmit

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy("Back to examiners on semester overview")

    def __get_success_message(self):
        return gettext_lazy("%(user)s was deactivated.") % {
            "user": self.relatedexaminer.user.get_full_name(),
        }

    def form_valid(self, form):
        self.relatedexaminer.active = False
        self.relatedexaminer.save()
        messages.success(self.request, self.__get_success_message())
        return super(DeactivateView, self).form_valid(form=form)


class ActivateView(SingleRelatedExaminerMixin, devilry_confirmview.View):
    def get_context_data(self, **kwargs):
        context = super(ActivateView, self).get_context_data(**kwargs)
        context["period"] = self.request.cradmin_role
        return context

    def get_pagetitle(self):
        return gettext_lazy("Re-activate examiner: %(user)s?") % {"user": self.relatedexaminer.user.get_full_name()}

    def get_submit_button_label(self):
        return gettext_lazy("Re-activate")

    def get_confirm_message(self):
        return gettext_lazy("Please confirm that you want to re-activate %(user)s.") % {
            "user": self.relatedexaminer.user.get_full_name()
        }

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy("Back to examiners on semester overview")

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appindexurl())

    def __get_success_message(self):
        return gettext_lazy("%(user)s was re-activated.") % {"user": self.relatedexaminer.user.get_full_name()}

    def form_valid(self, form):
        self.relatedexaminer.active = True
        self.relatedexaminer.save()
        messages.success(self.request, self.__get_success_message())
        return super(ActivateView, self).form_valid(form=form)


class AddExaminersTarget(devilry_multiselect2.user.Target):
    def get_submit_button_text(self):
        return gettext_lazy("Add selected examiners")


class AddView(devilry_multiselect2.user.BaseMultiselectUsersView):
    value_renderer_class = devilry_multiselect2.user.ItemValue
    template_name = "devilry_admin/period/examiners/add.django.html"
    model = User

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("add", kwargs={"filters_string": filters_string})

    def __get_userids_already_relatedexaminer_queryset(self):
        period = self.request.cradmin_role
        return RelatedExaminer.objects.filter(period=period).values_list("user_id", flat=True)

    def get_unfiltered_queryset_for_role(self, role):
        return (
            super(AddView, self)
            .get_unfiltered_queryset_for_role(role=self.request.cradmin_role)
            .exclude(id__in=self.__get_userids_already_relatedexaminer_queryset())
        )

    def get_target_renderer_class(self):
        return AddExaminersTarget

    def get_context_data(self, **kwargs):
        context = super(AddView, self).get_context_data(**kwargs)
        context["period"] = self.request.cradmin_role
        return context

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appindexurl())

    def __get_success_message(self, added_users):
        added_users_names = ['"{}"'.format(user.get_full_name()) for user in added_users]
        added_users_names.sort()
        return gettext_lazy("Added %(usernames)s.") % {"usernames": ", ".join(added_users_names)}

    def __create_relatedexaminers(self, selected_users):
        period = self.request.cradmin_role
        relatedexaminers = []
        for user in selected_users:
            relatedexaminer = RelatedExaminer(period=period, user=user)
            relatedexaminers.append(relatedexaminer)
        RelatedExaminer.objects.bulk_create(relatedexaminers)

    def form_valid(self, form):
        selected_users = list(form.cleaned_data["selected_items"])
        self.__create_relatedexaminers(selected_users=selected_users)
        messages.success(self.request, self.__get_success_message(added_users=selected_users))
        return super(AddView, self).form_valid(form=form)


class ImportExaminersView(bulkimport_users_common.AbstractTypeInUsersView):
    create_button_label = gettext_lazy("Bulk import examiners")

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy("Back to examiners on semester overview")

    def get_pagetitle(self):
        return gettext_lazy("Bulk import examiners")

    def import_users_from_emails(self, emails):
        period = self.request.cradmin_role
        result = RelatedExaminer.objects.bulk_create_from_emails(period=period, emails=emails)
        if result.new_relatedusers_was_created():
            messages.success(
                self.request,
                gettext_lazy("Added %(count)s new examiners to %(period)s.")
                % {"count": result.created_relatedusers_queryset.count(), "period": period.get_path()},
            )
        else:
            messages.warning(self.request, gettext_lazy("No new examiners was added."))

        if result.existing_relateduser_emails_set:
            messages.info(
                self.request,
                gettext_lazy("%(count)s users was already examiner on %(period)s.")
                % {"count": len(result.existing_relateduser_emails_set), "period": period.get_path()},
            )

    def import_users_from_usernames(self, usernames):
        period = self.request.cradmin_role
        result = RelatedExaminer.objects.bulk_create_from_usernames(period=period, usernames=usernames)
        if result.new_relatedusers_was_created():
            messages.success(
                self.request,
                gettext_lazy("Added %(count)s new examiners to %(period)s.")
                % {"count": result.created_relatedusers_queryset.count(), "period": period.get_path()},
            )
        else:
            messages.warning(self.request, gettext_lazy("No new examiners was added."))

        if result.existing_relateduser_usernames_set:
            messages.info(
                self.request,
                gettext_lazy("%(count)s users was already examiner on %(period)s.")
                % {"count": len(result.existing_relateduser_usernames_set), "period": period.get_path()},
            )


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^filter/(?P<filters_string>.+)?$", Overview.as_view(), name="filter"),
        crapp.Url(r"^deactivate/(?P<pk>\d+)$", DeactivateView.as_view(), name="deactivate"),
        crapp.Url(r"^activate/(?P<pk>\d+)$", ActivateView.as_view(), name="activate"),
        crapp.Url(r"^add/(?P<filters_string>.+)?$", AddView.as_view(), name="add"),
        crapp.Url(r"^importexaminers", ImportExaminersView.as_view(), name="importexaminers"),
    ]
