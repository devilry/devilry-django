from StringIO import StringIO  
from zipfile import ZipFile  
import tarfile
from django.http import HttpResponse  
from devilry.core.models import AssignmentGroup, Assignment
from django.utils.formats import date_format
from ui.defaults import DATETIME_FORMAT
from tarfile import TarFile
import copy

def create_zip_from_assignmentgroups(request, assignment, assignmentgroups):
    it = iter_streamable_archive(StreamableZip(), assignment, assignmentgroups)
    response = HttpResponse(it, mimetype="application/zip")
    response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
    return response

def create_tar_from_assignmentgroups(request, assignment, assignmentgroups):
    it = iter_streamable_archive(StreamableTar(), assignment, assignmentgroups)
    response = HttpResponse(it, mimetype="application/tar")  
    response["Content-Disposition"] = "attachment; filename=%s.tar" % assignment.get_path()  
    return response

class StreamableTar():
    def __init__(self):
        self.in_memory = StringIO()
        self.tar = DevilryTarfile.open(name=None, mode='w', fileobj=self.in_memory)
    
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
    as is if the last step doesn't divide on stop
    """
    l = []
    x = start
    while x <= stop:
        l.append(x)
        x += step
    if x > stop:
        l.append(stop)
    return l

def get_assignmentgroup_name(assigmentgroup):
    """
    Returns a string containing the group member of the
    assignmentgroup separated by '-'.
    """
    cands = assigmentgroup.get_candidates()
    cands = cands.replace(", ", "-")
    return cands

def get_dictionary_with_name_matches(assignmentgroups):
    """
    Takes a list of assignmentgroups and returns
    a dictionary containing the count of groups
    with similar names sa values in the dictionary.
    """
    matches = {}
    for assigmentgroup in assignmentgroups:
        name = get_assignmentgroup_name(assigmentgroup)
        if matches.has_key(name):
            matches[name] =  matches[name] + 1
        else:
            matches[name] = 1
    return matches

max_archive_chunk_size = 1000000

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

                # File size i greater than max_archive_chunk_size bytes
                # Add only chunks of data to the archive
                if f.size > max_archive_chunk_size and archive.can_write_chunks():
                    chunk_size = max_archive_chunk_size
                    start_index = 0
                    archive.start_filestream(filename, f.size)
                    for i in inclusive_range(chunk_size, f.size, chunk_size):
                        archive.append_file_chunk(bytes[start_index:i])
                        start_index += chunk_size
                        yield archive.get_bytes()
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

class DevilryTarfile(TarFile):
    def __init__(self, name=None, mode="r", fileobj=None):
        TarFile.__init__(self, name, mode, fileobj)
        self.filestream_active = False
    
    def start_filestream(self, tarinfo):
        """Add the TarInfo object `tarinfo' to the archive and opens a filestream.
        Data chunks are appended to the filestream with append_file_chunk, and
        the filestream must be closed with close_filestream.
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

        self.filestream_tarinfo = tarinfo
        self.filestream_active = True
        self.filestream_sum = 0
        self.filestream_name = tarinfo

    def append_file_chunk(self, fileobj, chunk_size):
        """
        Appends a chunk to the current active filestream started with start_filestream
        """
        self._check("aw")
        if not self.filestream_active:
            raise Exception("Cannot append file chunk without an active filestream."\
                            "Start a filestream first.")
        if fileobj is None:
            raise Exception("fileobj cannot be None.")

        tarfile.copyfileobj(fileobj, self.fileobj, chunk_size)
        self.offset += chunk_size
        self.filestream_sum += chunk_size
    
    def close_filestream(self):
        """
        Must be used to close a filestream session opened with start_filestream
        """
        if self.filestream_tarinfo.size != self.filestream_sum:
            raise Exception("Expected size of filestream %s has not been met."\
                            "Expected %d, but was %d."
                            % (filestream_tarinfo.name, self.filestream_tarinfo.size,
                               self.filestream_sum))
        blocks, remainder = divmod(self.filestream_tarinfo.size, tarfile.BLOCKSIZE)
        # Fill last block with zeroes
        if remainder > 0:
            zeroes_count = (tarfile.BLOCKSIZE - remainder)
            self.fileobj.write(tarfile.NUL * zeroes_count)
            self.offset += zeroes_count
        self.filestream_active = False
