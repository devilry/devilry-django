from devilry.adminscripts.dbsanity import dbsanity_registry

from dbsanity import (GradepluginsSanityCheck,
    AssignmentGroupSanityCheck, AssignmentSanityCheck)


dbsanity_registry.register(GradepluginsSanityCheck)
dbsanity_registry.register(AssignmentGroupSanityCheck)
dbsanity_registry.register(AssignmentSanityCheck)
