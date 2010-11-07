from StringIO import StringIO  
from zipfile import ZipFile  
from django.http import HttpResponse  
from devilry.core.models import AssignmentGroup, Assignment
from django.utils.formats import date_format
from ui.defaults import DATETIME_FORMAT
    
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

def create_zip_from_assignmentgroups2(request, assignment, assignmentgroups):
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
            if include_delivery_explanation:
                multiple_deliveries_content += "  %3d            %3d          %5d        %s\r\n" % \
                                               (delivery.number, len(metas), delivery_size,
                                                date_format(delivery.time_of_delivery, "DATETIME_FORMAT"))
        # Adding file explaining multiple deliveries
        if include_delivery_explanation:
            zip.writestr("%s/%s/%s" %
                         (assignment.get_path(), ass_group_name,
                          "Student has multiple deliveries.txt"),
                         multiple_deliveries_content.encode("ascii"))

    response = HttpResponse(mimetype="application/zip")  
    response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
    zip.close()         
    in_memory.seek(0)      
    response.write(in_memory.read())
    return response  


def create_zip_from_assignmentgroups(request, assignment, assignmentgroups):
    zip = False

    if zip:
        streamableZip = StreamableZip(assignment, assignmentgroups)
        response = HttpResponse(streamableZip.iter_files(), mimetype="application/zip")  
        response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
        return response
    else:
        streamableTar = StreamableTar(assignment, assignmentgroups)
        response = HttpResponse(streamableTar.iter_files(), mimetype="application/zip")  
        response["Content-Disposition"] = "attachment; filename=%s.tar" % assignment.get_path()  
        return response


class StreamableZip():
    def __init__(self, assignment, assignmentgroups):
        self.assignment = assignment
        self.assignmentgroups = assignmentgroups
        self.in_memory = StringIO()
        self.zip = ZipFile(self.in_memory, "w")
        self.name_matches = get_dictionary_with_name_matches(assignmentgroups)
        self.nextcount = 0
        self.iter_done = False
    
    def iter_files(self):
        # Finished iterating all the files
        if self.iter_done:
            raise StopIteration()

        for ass_group in self.assignmentgroups:
            ass_group_name = get_assignmentgroup_name(ass_group)
            # If multiple groups with the same members exists,
            # postfix the name with asssignmengroup ID.
            if self.name_matches[ass_group_name] > 1:
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
                        self.zip.writestr("%s/%s/%d/%s" % (self.assignment.get_path(), ass_group_name,
                                                      delivery.number, f.filename), bytes)
                    else:
                        self.zip.writestr("%s/%s/%s" % (self.assignment.get_path(), ass_group_name,
                                                   f.filename), bytes)
                    yield self.in_memory.read()
                if include_delivery_explanation:
                    multiple_deliveries_content += "  %3d            %3d          %5d        %s\r\n" % \
                                               (delivery.number, len(metas), delivery_size,
                                                date_format(delivery.time_of_delivery, "DATETIME_FORMAT"))
            # Adding file explaining multiple deliveries
            if include_delivery_explanation:
                self.zip.writestr("%s/%s/%s" %
                             (self.assignment.get_path(), ass_group_name,
                              "Student has multiple deliveries.txt"),
                             multiple_deliveries_content.encode("ascii"))
        self.iter_done = True
        self.zip.close()
        self.in_memory.seek(0)
        yield self.in_memory.read()


import tarfile

class StreamableTar():
    def __init__(self, assignment, assignmentgroups):
        self.assignment = assignment
        self.assignmentgroups = assignmentgroups
        self.in_memory = StringIO()
        self.tar = tarfile.open(name=None, mode='w', fileobj=self.in_memory)
        self.name_matches = get_dictionary_with_name_matches(assignmentgroups)
        self.nextcount = 0
        self.iter_done = False
    
    def iter_files(self):
        # Finished iterating all the files
        if self.iter_done:
            raise StopIteration()

        for ass_group in self.assignmentgroups:
            ass_group_name = get_assignmentgroup_name(ass_group)
            # If multiple groups with the same members exists,
            # postfix the name with asssignmengroup ID.
            if self.name_matches[ass_group_name] > 1:
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
                    filename = "%s/%s/%s" % (self.assignment.get_path(), ass_group_name,
                                             f.filename)
                    if include_delivery_explanation:
                        filename = "%s/%s/%d/%s" % (self.assignment.get_path(), ass_group_name,
                                                    delivery.number, f.filename)
                    file_to_add = tarfile.TarInfo(filename)
                    file_to_add.size = len(bytes)
                    self.tar.addfile(file_to_add, StringIO(bytes))
                    print "yield ", f.filename
                    yield self.in_memory.read()

                if include_delivery_explanation:
                    multiple_deliveries_content += "  %3d            %3d          %5d        %s\r\n" % \
                                               (delivery.number, len(metas), delivery_size,
                                                date_format(delivery.time_of_delivery, "DATETIME_FORMAT"))
            # Adding file explaining multiple deliveries
            if include_delivery_explanation:
                bytes = multiple_deliveries_content.encode("ascii")
                file_to_add = tarfile.TarInfo("%s/%s/%s" %
                             (self.assignment.get_path(), ass_group_name,
                              "Student has multiple deliveries.txt"))
                file_to_add.size = len(bytes)
                self.tar.addfile(file_to_add, StringIO(bytes))
        
        self.iter_done = True
        self.tar.close()
        self.in_memory.seek(0)
        yield self.in_memory.read()
