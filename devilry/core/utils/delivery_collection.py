from django.utils.formats import date_format
from django.http import HttpResponse  
from django.conf import settings

from devilry.core.models import AssignmentGroup, Assignment
from devilry.ui.defaults import DATETIME_FORMAT

from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
import tarfile, copy

def create_archive_from_assignmentgroups(request, assignment, assignmentgroups, archive_type):

    if archive_type == 'zip':
        it = iter_archive_assignmentgroups(StreamableZip(), assignment, assignmentgroups)
        response = HttpResponse(it, mimetype="application/zip")
        response["Content-Disposition"] = "attachment; filename=%s.zip" % assignment.get_path()  
    elif archive_type == 'tar':
        it = iter_archive_assignmentgroups(StreamableTar(), assignment, assignmentgroups)
        response = HttpResponse(it, mimetype="application/tar")  
        response["Content-Disposition"] = "attachment; filename=%s.tar" % assignment.get_path()  
    else:
        raise Exception("archive_type is invalid:%s" % archive_type)
    return response


def create_archive_from_delivery(request, delivery, archive_type):
    group = delivery.assignment_group
    assignment = group.parentnode
    group_name = get_assignmentgroup_name(group)
    it = iter_archive_deliveries(StreamableTar(), assignment.get_path(), group_name, [delivery])
    response = HttpResponse(it, mimetype="application/tar")  
    response["Content-Disposition"] = "attachment; filename=%s.tar" % assignment.get_path()  
    return response


def verify_groups_not_exceeding_max_file_size(groups):
    for g in groups:
        verify_deliveries_not_exceeding_max_file_size(g.deliveries.all())

def verify_deliveries_not_exceeding_max_file_size(deliveries):
    max_size = settings.MAX_ARCHIVE_CHUNK_SIZE
    for d in deliveries:
        for f_meta in d.filemetas.all():
            if f_meta.size > max_size:
                raise Exception()


class MemoryIO(object):
    """
    A simple in-memory implementation of IO with read/write/seek/tell
    implemented.
    """
    def __init__(self, initial_bytes=None):
        self.buffer = str()
        self.pos = 0
        if not initial_bytes == None:
            self.buffer = str(initial_bytes)
            self.pos = len(initial_bytes)
            
    def tell(self):
        """Always returns 0"""
        return self.pos

    def seek(self, n):
        self.pos = n
        return None

    def flush(self):
        """Does nothing"""
        pass

    def read(self, n = -1):
        """
        Read n bytes from the buffer. If n is not used, the entire
        content is returned. The read content is deleted from memory.
        The pos variable is deliberately not updated.
        """
        if len(self.buffer) == 0:
            return str()
        buf = None
        if n == -1:
            buf = self.buffer
            self.buffer = str()
        else:
            buf = self.buffer[:n]
            self.buffer = self.buffer[n:]
        return buf

    def write(self, bytes):
        """
        Append the bytes to the in-memory buffer.
        """
        self.buffer += str(bytes)
        self.pos += len(bytes)
        return len(bytes)


class StreamableTar(object):
    def __init__(self):
        self.in_memory = MemoryIO()
        self.tar = DevilryTarfile.open(name=None, mode='w:gz', fileobj=self.in_memory)
    
    def add_file(self, filename, bytes):
        tarinfo = tarfile.TarInfo(filename)
        tarinfo.size = len(bytes)
        self.tar.addfile(tarinfo, MemoryIO(bytes))

    def start_filestream(self, filename, filesize):
        tarinfo = tarfile.TarInfo(filename)
        tarinfo.size = filesize
        self.tar.start_filestream(tarinfo)

    def append_file_chunk(self, bytes, chunk_size):
        self.tar.append_file_chunk(MemoryIO(bytes), chunk_size)

    def close_filestream(self):
        self.tar.close_filestream()
    
    def read(self):
        self.in_memory.seek(0)
        bytes = self.in_memory.read()
        return bytes

    def close(self):
        self.tar.close()
    
    def can_write_chunks(self):
        return True


class StreamableZip(object):
    def __init__(self):
        self.in_memory =  MemoryIO()
        self.zip = ZipFile(self.in_memory, "w", compression=ZIP_DEFLATED)
        
    def add_file(self, filename, bytes):
         self.zip.writestr(filename, bytes)

    def read(self):
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


def iter_archive_deliveries(archive, assignment_path, group_name, deliveries):
    include_delivery_explanation = False
    if len(deliveries) > 1:
        include_delivery_explanation = True
        multiple_deliveries_content = "Delivery-ID    File count    Total size     Delivery time  \r\n"

    for delivery in deliveries:
        metas = delivery.filemetas.all()
        delivery_size = 0
        for f in metas:
            delivery_size += f.size
            filename = "%s/%s/%s" % (assignment_path, group_name,
                                 f.filename)
            if include_delivery_explanation:
                filename = "%s/%s/%d/%s" % (assignment_path, group_name,
                                                delivery.number, f.filename)
            # File size i greater than MAX_ARCHIVE_CHUNK_SIZE bytes
            # Write only chunks of size MAX_ARCHIVE_CHUNK_SIZE to the archive
            if f.size > settings.MAX_ARCHIVE_CHUNK_SIZE:
                if not archive.can_write_chunks():
                    raise Exception("The size of file %s is greater than the maximum allowed size. "\
                                    "Download stream aborted.")
                chunk_size = settings.MAX_ARCHIVE_CHUNK_SIZE
                # Open file stream for reading
                file_to_stream = f.read_open()
                # Start a filestream in the archive
                archive.start_filestream(filename, f.size)
                for i in inclusive_range(chunk_size, f.size, chunk_size):
                    bytes = file_to_stream.read(chunk_size)
                    archive.append_file_chunk(bytes, len(bytes))
                    #Read the chunk from the archive and yield the data
                    yield archive.read()
                archive.close_filestream()
            else:
                bytes = f.read_open().read(f.size)
                archive.add_file(filename, bytes)
                #Read the content from the streamable archive and yield the data
                yield archive.read()            
        if include_delivery_explanation:
            multiple_deliveries_content += "  %3d            %3d          %5d        %s\r\n" % \
                                           (delivery.number, len(metas), delivery_size,
                                            date_format(delivery.time_of_delivery, "DATETIME_FORMAT"))
    # Adding file explaining multiple deliveries
    if include_delivery_explanation:
        archive.add_file("%s/%s/%s" %
                         (assignment_path, group_name,
                          "Deliveries.txt"),
                         multiple_deliveries_content.encode("ascii"))


def iter_archive_assignmentgroups(archive, assignment, assignmentgroups):
    """
    Creates an archive, adds files delivered by the assignmentgroups
    and yields the data.
    """
    name_matches = get_dictionary_with_name_matches(assignmentgroups)
    for group in assignmentgroups:
        group_name = get_assignmentgroup_name(group)
        # If multiple groups with the same members exists,
        # postfix the name with assignmentgroup ID.
        if name_matches[group_name] > 1:
            group_name = "%s+%d" % (group_name, group.id)
        deliveries = group.deliveries.all()
        for bytes in iter_archive_deliveries(archive, assignment.get_path(), group_name, deliveries):
            yield bytes
    archive.close()
    yield archive.read()


class DevilryTarfile(tarfile.TarFile):
    """
    tarfile does not directly support streaming chunks to the file.
    might be solved by letting the read method of the file-like class
    just return chunks instead of the entire file.
    """
    def __init__(self, name=None, mode="r", fileobj=None):
        tarfile.TarFile.__init__(self, name, mode, fileobj)
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
            raise Exception("Expected size of filestream %s has not been met. "\
                            "Expected %d, but was %d."
                            % (self.filestream_tarinfo.name, self.filestream_tarinfo.size,
                               self.filestream_sum))
        blocks, remainder = divmod(self.filestream_tarinfo.size, tarfile.BLOCKSIZE)
        # Fill last block with zeroes
        if remainder > 0:
            zeroes_count = (tarfile.BLOCKSIZE - remainder)
            self.fileobj.write(tarfile.NUL * zeroes_count)
            self.offset += zeroes_count
        self.filestream_active = False
