from django.views.generic import TemplateView
import restful


class MainView(TemplateView):
    template_name='administrator/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        return context
