from devilry.adminscripts.dbsanity import (DbSanityCheck, dbsanity_registry)
from devilry.core.gradeplugin import registry, get_registry_key
from devilry.core.models import Period

from models import RstSchemaGrade, RstSchemaDefinition


class RstGradeDbSanityCheck(DbSanityCheck):
    @classmethod
    def get_label(cls):
        return registry.getitem_from_cls(RstSchemaGrade).label

    def check(self):
        for rg in RstSchemaGrade.objects.all():
            feedback_obj = rg.get_feedback_obj()
            points = rg._parse_points()
            if points != rg.points:
                self.add_autofixable_error("%s has incorrect points." % rg)

        schemadef_ok = True
        for schemadef in RstSchemaDefinition.objects.all():
            correct = schemadef._parse_max_points() 
            if schemadef.maxpoints != correct:
                self.add_autofixable_error(
                        "%s has incorrect maxpoints. Current: %s. "\
                        "Should be: %s." % (schemadef, schemadef.maxpoints,
                            correct))
                schemadef_ok = False

        if schemadef_ok:
            periods = Period.objects.filter(
                    assignments__grade_plugin=get_registry_key(RstSchemaGrade))
            for period in periods:
                for schemadef, percent in RstSchemaDefinition.get_percents(period):
                    if int(schemadef.percent) != int(percent):
                        self.add_autofixable_error(
                                "%s has incorrect percent. Current: %.2f%%. "\
                                "Should be: %.2f%%." % (schemadef,
                                    schemadef.percent, percent))
        else:
            self.add_autofixable_error(
                    "Will not check percents because tests on "\
                    "required fields failed.")

    @classmethod
    def fix(cls):
        for rg in RstSchemaGrade.objects.all():
            rg.save()
        for schemadef in RstSchemaDefinition.objects.all():
            schemadef.save()
        periods = Period.objects.filter(
                assignments__grade_plugin=get_registry_key(RstSchemaGrade))
        for period in periods:
            RstSchemaDefinition.recalculate_percents(period)
