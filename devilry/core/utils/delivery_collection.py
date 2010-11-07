from StringIO import StringIO  
from zipfile import ZipFile  
import tarfile
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
        it = iter_streamable_archive(StreamableZip(), assignment, assignmentgroups)
        response = HttpResponse(it, mimetype="application/zip")
        response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
        return response
    else:
        it = iter_streamable_archive(StreamableTar(), assignment, assignmentgroups)
        response = HttpResponse(it, mimetype="application/tar")  
        response["Content-Disposition"] = "attachment; filename=%s.tar" % assignment.get_path()  
        return response


class StreamableTar():
    def __init__(self):
        self.in_memory = StringIO()
        self.tar = DevilryTarfile.open(name=None, mode='w', fileobj=self.in_memory)
        #self.tar = tarfile.open(name=None, mode='w', fileobj=self.in_memory)
        
    def add_file(self, filename, bytes):
        tarinfo = tarfile.TarInfo(filename)
        tarinfo.size = len(bytes)
        self.tar.addfile(tarinfo, StringIO(bytes))

    def start_filestream(self, filename, filesize):
        tarinfo = tarfile.TarInfo(filename)
        tarinfo.size = filesize
        self.tar.start_filestream(tarinfo)

    def append_file_chunk(self, bytes):
        self.tar.append_file_chunk(StringIO(bytes), len(bytes))

    def close_filestream(self):
        self.tar.close_filestream()
    
    def get_bytes(self):
        return self.in_memory.read()

    def close(self):
        self.tar.close()
        self.in_memory.seek(0)

    def can_write_chunks(self):
        return True

class StreamableZip():
    def __init__(self):
        self.in_memory = StringIO()
        self.zip = ZipFile(self.in_memory, "w")
        
    def add_file(self, filename, bytes):
         self.zip.writestr(filename, bytes)

    def get_bytes(self):
        return self.in_memory.read()

    def close(self):
        self.zip.close()
        self.in_memory.seek(0)
    
    def can_write_chunks(self):
        return False


def inclusive_range(start, stop, step=1):
    """
    A range() clone, but this includes the right limit
    as is if it doesn't divide on stop
    """
    l = []
    x = start
    while x <= stop:
        l.append(x)
        x += step
    if x > stop:
        l.append(stop)
    return l

def iter_streamable_archive(archive, assignment, assignmentgroups):
    name_matches = get_dictionary_with_name_matches(assignmentgroups)
    iter_done = False
    
    # Finished iterating all the files
    if iter_done:
        raise StopIteration()

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

                filename = "%s/%s/%s" % (assignment.get_path(), ass_group_name,
                                         f.filename)
                if include_delivery_explanation:
                    filename = "%s/%s/%d/%s" % (assignment.get_path(), ass_group_name,
                                                delivery.number, f.filename)

                print "Adding file ", filename

                #greater than 1000 bytes, write chuncks of 100
                if f.size > 1000000 and archive.can_write_chunks():
                    chunk_size = 100000
                    start_index = 0
                    print "file size is bigger than 1000 bytes:", f.size
                    archive.start_filestream(filename, f.size)
                    for i in inclusive_range(chunk_size, f.size, chunk_size):
                        print "append   chunk: byte[%d:%d]" % (start_index, i)
                        archive.append_file_chunk(bytes[start_index:i])
                        start_index += chunk_size
                    archive.close_filestream()
                else:
                    archive.add_file(filename, bytes)

                yield archive.get_bytes()
            if include_delivery_explanation:
                multiple_deliveries_content += "  %3d            %3d          %5d        %s\r\n" % \
                                               (delivery.number, len(metas), delivery_size,
                                                date_format(delivery.time_of_delivery, "DATETIME_FORMAT"))
        # Adding file explaining multiple deliveries
        if include_delivery_explanation:
            archive.add_file("%s/%s/%s" %
                                  (assignment.get_path(), ass_group_name,
                                   "Student has multiple deliveries.txt"),
                                  multiple_deliveries_content.encode("ascii"))
    iter_done = True
    archive.close()
    yield archive.get_bytes()

from tarfile import TarFile
import copy

class DevilryTarfile(TarFile):

    def __init__(self, name=None, mode="r", fileobj=None):
        TarFile.__init__(self, name, mode, fileobj)
        self.filestream_active = False
        
    
    def addfile(self, tarinfo, fileobj):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
        given, tarinfo.size bytes are read from it and added to the archive.
        You can create TarInfo objects using gettarinfo().
           On Windows platforms, `fileobj' should always be opened with mode
           'rb' to avoid irritation about the file size.
           """
        self._check("aw")

        if self.filestream_active:
            raise Exception("Cannot add new file in the middle of a filestream")
        
        tarinfo = copy.copy(tarinfo)

        buf = tarinfo.tobuf(self.posix)
        self.fileobj.write(buf)
        self.offset += len(buf)

        # If there's data to follow, append it.
        if fileobj is not None:
            tarfile.copyfileobj(fileobj, self.fileobj, tarinfo.size)
            blocks, remainder = divmod(tarinfo.size, tarfile.BLOCKSIZE)
            if remainder > 0:
                self.fileobj.write(tarfile.NUL * (tarfile.BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * tarfile.BLOCKSIZE

        self.members.append(tarinfo)


    def start_filestream(self, tarinfo):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
        given, tarinfo.size bytes are read from it and added to the archive.
        You can create TarInfo objects using gettarinfo().
           On Windows platforms, `fileobj' should always be opened with mode
           'rb' to avoid irritation about the file size.
           """
        self._check("aw")
        if self.filestream_active:
            raise Exception("Cannot start a new filestream in the middle of a filestream."\
                            "Close active stream first.")
        tarinfo = copy.copy(tarinfo)
        buf = tarinfo.tobuf(self.posix)
        self.fileobj.write(buf)
        self.offset += len(buf)
        self.members.append(tarinfo)

        self.last_file_size = tarinfo.size
        self.filestream_active = True

"""
    def append_file_chunk1(self, fileobj, write_count, last_chunk):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
        given, tarinfo.size bytes are read from it and added to the archive.
        You can create TarInfo objects using gettarinfo().
           On Windows platforms, `fileobj' should always be opened with mode
           'rb' to avoid irritation about the file size.
           """
        self._check("aw")

        if not self.filestream_active:
            raise Exception("Cannot append file chunk without an active filestream."\
                            " Start a filestream first.")
        # If there's data to follow, append it.
        if fileobj is not None:
            tarfile.copyfileobj(fileobj, self.fileobj, write_count)
            print "writing bytes to obj:", write_count
            
            if last_chunk:
                print "WRITING LAST CHUNK"
                
                if self.last_file_size == -1:
                    print "last_file_size was -1 and should not be!!"
                
                blocks, remainder = divmod(self.last_file_size, tarfile.BLOCKSIZE)
                
                if remainder > 0:
                    self.fileobj.write(tarfile.NUL * (tarfile.BLOCKSIZE - remainder))
                    blocks += 1
                    print "Append 0s:", (tarfile.BLOCKSIZE - remainder)
                self.offset += blocks * tarfile.BLOCKSIZE

                print "Offset:", self.offset
                print "increase offset with ", (blocks * tarfile.BLOCKSIZE)
                self.last_file_size = -1
                self.filestream_active = False
"""

    def append_file_chunk(self, fileobj, chunk_size):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
        given, tarinfo.size bytes are read from it and added to the archive.
        You can create TarInfo objects using gettarinfo().
           On Windows platforms, `fileobj' should always be opened with mode
           'rb' to avoid irritation about the file size.
           """
        self._check("aw")

        if not self.filestream_active:
            raise Exception("Cannot append file chunk without an active filestream."\
                            "Start a filestream first.")
        # If there's data to follow, append it.
        if fileobj is not None:
            tarfile.copyfileobj(fileobj, self.fileobj, chunk_size)
            self.offset += write_coun
    
    def close_filestream(self):
        blocks, remainder = divmod(self.last_file_size, tarfile.BLOCKSIZE)
        # Fill last block with zeroes
        if remainder > 0:
            zeroes_count = (tarfile.BLOCKSIZE - remainder)
            self.fileobj.write(tarfile.NUL * zeroes_count)
            self.offset += zeroes_count
        self.filestream_active = False
