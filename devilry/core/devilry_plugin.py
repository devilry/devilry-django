from devilry.adminscripts.dbsanity import dbsanity_registry

from dbsanity import (GradepluginsSanityCheck,
    AssignmentGroupSanityCheck)


dbsanity_registry.register(GradepluginsSanityCheck)
dbsanity_registry.register(AssignmentGroupSanityCheck)
