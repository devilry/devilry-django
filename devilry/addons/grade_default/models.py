from django.db import models
from devilry.core.gradeplugin import GradeModel

class CharFieldGrade(GradeModel):
    grade = models.CharField(max_length=15)

    def get_short_string(self, feedback_obj):
        return self.grade

    def set_grade_from_xmlrpcstring(self, grade, feedback_obj):
        self.grade = grade

    def get_grade_as_xmlrpcstring(self, feedback_obj):
        return self.grade
