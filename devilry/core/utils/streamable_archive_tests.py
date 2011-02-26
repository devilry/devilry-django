#!/usr/bin/env python
"""
Creats an archive with deliveries.
"""

from devilry.core.models import (Assignment, AssignmentGroup)
from devilry.core.utils.delivery_collection import create_archive_from_assignmentgroups
from devilry.core.utils.stream_archives import  MemoryIO 

import sys

if __name__ == '__main__':

    archive_type = "tar" 
    filename = "test." + archive_type

    if len(sys.argv) == 2 and sys.argv[1] == "all":
        ass_groups_all = []
        assignments = Assignment.objects.all()
        for assignment in assignments:
            for assignmentgroup in assignment.assignmentgroups.all():
                ass_groups_all.append(assignmentgroup)
        assignmentgroups = ass_groups_all
    else:
        assignment = Assignment.objects.get(id=48)
        assignmentgroups = []
        assignmentgroups.append(AssignmentGroup.objects.get(id=8091))
        assignmentgroups.append(AssignmentGroup.objects.get(id=8095))
        assignmentgroups.append(AssignmentGroup.objects.get(id=8121))
        assignmentgroups.append(AssignmentGroup.objects.get(id=8145))

        assignmentgroups = assignment.assignmentgroups.all()
        
    print "Building %s with %d assignmentgroups" % (archive_type, len(assignmentgroups))
    iterator = create_archive_from_assignmentgroups(None, assignmentgroups,
                                                    assignment.get_path(),
                                                    archive_type)
    f = open(filename, "w")
    for bytes in iterator:
        f.write(bytes)
    f.close
        
    print "Wrote to %s" % filename
