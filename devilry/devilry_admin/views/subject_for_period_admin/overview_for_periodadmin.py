

from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter

from devilry.apps.core.models import Period
from devilry.devilry_cradmin import devilry_listbuilder



class PeriodItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'period'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='overview',
            roleid=self.period.id,
            viewname=crapp.INDEXVIEW_NAME
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-period-overview-perioditemframe']


class Overview(listbuilderview.FilterListMixin, listbuilderview.View):
    template_name = 'devilry_admin/subject/overview_for_period_admins.html'
    model = Period
    frame_renderer_class = PeriodItemFrame
    value_renderer_class = devilry_listbuilder.period.AdminItemValue

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            modelfields=[
                'long_name',
                'short_name',
            ],
            label_is_screenreader_only=True
        ))

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        subject = self.request.cradmin_role
        return Period.objects.filter_user_is_admin(user=self.request.user).filter(parentnode=subject)\
            .order_by('-start_time')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
