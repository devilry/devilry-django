from devilry.devilry_dumpv2database import modeldumper
from devilry.devilry_qualifiesforexam.models import Status, QualifiesForFinalExam


class QualifiesForExamStatusDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Status

    def optimize_queryset(self, queryset):
        queryset = queryset.select_related('user', 'period')
        return queryset
    
    def serialize_model_object(self, obj):
        serialized = super(QualifiesForExamStatusDumper, self).serialize_model_object(obj=obj)
        return serialized


class QualifiesForFinalExamDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return QualifiesForFinalExam

    def optimize_queryset(self, queryset):
        queryset = queryset.select_related('relatedstudent', 'status')
        return queryset
    
    def serialize_model_object(self, obj):
        serialized = super(QualifiesForFinalExamDumper, self).serialize_model_object(obj=obj)
        return serialized
