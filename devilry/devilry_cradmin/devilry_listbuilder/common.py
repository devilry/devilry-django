from django_cradmin.viewhelpers import listbuilder


class GoForwardLinkItemFrame(listbuilder.itemframe.Link):
    template_name = 'devilry_cradmin/common/goforwardlinkitemframe.django.html'

    def get_extra_css_classes_list(self):
        return ['devilry-django-cradmin-listbuilder-itemframe-goforward']
