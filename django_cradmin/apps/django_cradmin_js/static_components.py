import django_cradmin
from django_cradmin import javascriptregistry


class CradminJavascript(javascriptregistry.component.AbstractJsComponent):
    @classmethod
    def get_component_id(cls):
        return "django_cradmin_javascript"

    def get_sourceurls(self):
        return [
            self.get_static_url(
                "django_cradmin_js/{version}/django_cradmin_all.js".format(version=django_cradmin.__version__)
            )
        ]
