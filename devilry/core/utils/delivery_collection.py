from StringIO import StringIO  
from zipfile import ZipFile  
from django.http import HttpResponse  
from devilry.core.models import AssignmentGroup, Assignment
from django.utils.formats import date_format

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

    from ui.defaults import DATETIME_FORMAT

    in_memory = StringIO()  
    zip = ZipFile(in_memory, "a")

    for ass_group in assignmentgroups:
        ass_group_name = get_assignmentgroup_name(ass_group)
        # If multiple groups with the same members exists,
        # postfix the name with asssignmengroup ID.
        if name_matches[ass_group_name] > 1:
            ass_group_name = "%s+%d" % (ass_group_name, ass_group.id)

        include_delivery_explanation = False
        deliveries = ass_group.deliveries.all()
        if len(deliveries) > 1:
            include_delivery_explanation = True
            multiple_deliveries_content = "Delivery-ID    File count    Total size     Delivery time  \r\n"
            
        for delivery in deliveries:
            metas = delivery.filemetas.all()
            delivery_size = 0
            for f in metas:
                delivery_size += f.size
                bytes = f.read_open().read(f.size)
                if include_delivery_explanation:
                    zip.writestr("%s/%s/%d/%s" % (assignment.get_path(), ass_group_name,
                                                  delivery.number, f.filename), bytes)
                else:
                    zip.writestr("%s/%s/%s" % (assignment.get_path(), ass_group_name,
                                               f.filename), bytes)
            multiple_deliveries_content += "  %3d            %3d          %5d        %s\r\n" % \
                                           (delivery.number, len(metas), delivery_size,
                                            date_format(delivery.time_of_delivery, "DATETIME_FORMAT"))
        # Adding file explaining multiple deliveries
        if include_delivery_explanation:
            zip.writestr("%s/%s/%s" %
                         (assignment.get_path(), ass_group_name,
                          "Student has multiple deliveries.txt"),
                         multiple_deliveries_content.encode("ascii"))
    # fix for Linux zip files read in Windows  
    for file in zip.filelist:  
        file.create_system = 0      
    zip.close()  

    response = HttpResponse(mimetype="application/zip")  
    response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
         
    in_memory.seek(0)      
    response.write(in_memory.read())  
    return response  
