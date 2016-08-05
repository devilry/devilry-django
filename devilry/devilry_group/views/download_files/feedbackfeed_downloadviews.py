from django.http import HttpResponseRedirect
from django_cradmin import crapp

from devilry.devilry_cradmin.viewhelpers.devilry_confirmview import View


class WaitForDownload(View):
    """
    Redirected to this view when downloading files.
    """
    # def get(self, request, *args, **kwargs):
    #     """
    #
    #     Args:
    #         request:
    #         *args:
    #         **kwargs:
    #
    #     Returns:
    #
    #     """
    #     print args

    def get_confirm_message(self):
        return 'Wait while zipping and preparing download'

    def get_submit_button_label(self):
        return 'back'

    def get_backlink_label(self):
        return ''

    def get_backlink_url(self):
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^wait-for-download//(?P<pk>\d+)$',
            WaitForDownload.as_view(),
            name='wait-for-download'
        )
    ]
