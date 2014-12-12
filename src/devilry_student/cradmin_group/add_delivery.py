from django.views.generic import TemplateView

from django_cradmin import crapp


class AddDeliveryView(TemplateView):
    template_name = 'devilry_student/cradmin_group/add_delivery.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', AddDeliveryView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
