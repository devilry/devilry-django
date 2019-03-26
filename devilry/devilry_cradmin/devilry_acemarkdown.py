from cradmin_legacy.acemarkdown.widgets import AceMarkdownWidget


class Default(AceMarkdownWidget):
    template_name = 'devilry_cradmin/devilry_acemarkdown.django.html'
    extra_css_classes = ''

    def get_context(self, *args, **kwargs):
        context = super(Default, self).get_context(*args, **kwargs)
        context.update({
            'extra_css_classes': self.extra_css_classes
        })
        return context


class Large(Default):
    """
    Large ace markdown widget.
    """
    extra_css_classes = 'devilry-ace-editor--large'


class Small(Default):
    """
    Small ace markdown widget.
    """
    extra_css_classes = 'devilry-ace-editor--small'
