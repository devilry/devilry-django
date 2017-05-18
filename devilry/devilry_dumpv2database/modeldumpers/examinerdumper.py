from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Examiner


class ExaminerDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Examiner
