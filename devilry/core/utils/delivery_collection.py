from StringIO import StringIO  
from zipfile import ZipFile  
from django.http import HttpResponse  
from devilry.core.models import AssignmentGroup, Assignment

def get_assignmentgroup_name(assigmentgroup):
     cands = assigmentgroup.get_candidates()
     cands = cands.replace(", ", "-")
     return cands

def get_dictionary_with_name_matches(assignmentgroups):
    matches = {}
    for assigmentgroup in assignmentgroups:
        name = get_assignmentgroup_name(assigmentgroup)
        if matches.has_key(name):
            matches[name] =  matches[name] + 1
        else:
            matches[name] = 1
    return matches

def create_zip_from_assignmentgroups(request, assignment, assignmentgroups):
    name_matches = get_dictionary_with_name_matches(assignmentgroups)

    in_memory = StringIO()  
    zip = ZipFile(in_memory, "a")  

    for ass_group in assignmentgroups:
        ass_group_name = get_assignmentgroup_name(ass_group)
        # If multiple groups with the same members exists,
        # postfix the name with asssignmengroup ID.
        if name_matches[ass_group_name] > 1:
            ass_group_name = "%s+%d" % (ass_group_name, ass_group.id)
        
        deliveries = ass_group.deliveries.all()
        for delivery in deliveries:
            metas = delivery.filemetas.all()
            for f in metas:
                bytes = f.read_open().read(f.size)
                zip.writestr("%s/%s/%d/%s" % (assignment.get_path(), ass_group_name, delivery.number,
                                              f.filename), bytes)
    # fix for Linux zip files read in Windows  
    for file in zip.filelist:  
        file.create_system = 0      
    zip.close()  

    response = HttpResponse(mimetype="application/zip")  
    response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
         
    in_memory.seek(0)      
    response.write(in_memory.read())  
    return response  
