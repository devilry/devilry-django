from devilry.adminscripts.dbsanity import dbsanity_registry

from dbsanity import (GradepluginsSanityCheck,
    AssignmentGroupStatusSanityCheck)


dbsanity_registry.register(GradepluginsSanityCheck)
dbsanity_registry.register(AssignmentGroupStatusSanityCheck)
