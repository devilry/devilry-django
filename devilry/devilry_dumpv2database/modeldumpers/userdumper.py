from django.contrib.auth import get_user_model

from devilry.devilry_dumpv2database import modeldumper


class UserDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return get_user_model()
