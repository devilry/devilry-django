from cradmin_legacy import crapp

from devilry.devilry_admin.views.assignment.examiners import base_single_examinerview
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_admin.views.assignment.students.overview import RowListWithMatchResults


class ExaminerDetailsView(groupview_base.BaseInfoView, base_single_examinerview.SingleExaminerViewMixin):
    filterview_name = crapp.INDEXVIEW_NAME
    template_name = "devilry_admin/assignment/examiners/examinerdetails.django.html"
    listbuilder_class = RowListWithMatchResults

    #
    # Add support for showing results on the top of the list.
    #
    def get_listbuilder_list_kwargs(self):
        kwargs = super().get_listbuilder_list_kwargs()
        kwargs["num_matches"] = self.num_matches or 0
        kwargs["num_total"] = self.num_total or 0
        kwargs["page"] = self.request.GET.get("page", 1)
        return kwargs

    def get_unfiltered_queryset_for_role(self, role):
        queryset = (
            super(ExaminerDetailsView, self)
            .get_unfiltered_queryset_for_role(role=role)
            .filter(examiners__relatedexaminer=self.get_relatedexaminer())
        )

        # Set unfiltered count on self.
        self.num_total = queryset.count()
        return queryset

    def get_queryset_for_role(self, role):
        queryset = super().get_queryset_for_role(role=role)

        # Set filtered count on self.
        self.num_matches = queryset.count()
        return queryset

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME,
            kwargs={"filters_string": filters_string, "relatedexaminer_id": self.get_relatedexaminer_id()},
        )

    def get_context_data(self, **kwargs):
        context = super(ExaminerDetailsView, self).get_context_data(**kwargs)
        context["relatedexaminer"] = self.get_relatedexaminer()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r"^(?P<relatedexaminer_id>\d+)/(?P<filters_string>.+)?$",
            ExaminerDetailsView.as_view(),
            name=crapp.INDEXVIEW_NAME,
        ),
    ]
