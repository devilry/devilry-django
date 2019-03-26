from django.views.generic import TemplateView
from cradmin_legacy import crapp

from devilry.devilry_frontpage.cradminextensions.listbuilder import listbuilder_role


class FrontpageView(TemplateView):
    template_name = 'devilry_frontpage/frontpage.django.html'

    def __make_roleselect_list(self):
        return listbuilder_role.RoleSelectList(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)
        context['roleselect_list'] = self.__make_roleselect_list()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', FrontpageView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
