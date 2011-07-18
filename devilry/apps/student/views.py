from django.views.generic import TemplateView

import restful


class MainView(TemplateView):
    template_name='student/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        context['restfulclasses'] = [getattr(restful, restclsname) for restclsname in restful.__all__]

        #print restful.RestfulSimplifiedAssignment._meta.simplified._meta.model.objects.all()
        
        return context
