from django.apps import AppConfig


class WithoutStyleguideAppConfig(AppConfig):
    default = True
    name = "django_cradmin.apps.django_cradmin_styles"
    verbose_name = "Django cradmin styles"
