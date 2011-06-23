from zipfile import ZipFile, ZIP_DEFLATED
import tarfile, copy

class MemoryIO(object):
    """
    An in-memory file like IO implementation with read, write,
    seek and tell implemented. Content read is deleted from
    memory to keep the memory consumption a a minimum.
    """
    def __init__(self, initial_bytes=None):
        self.buffer = str()
        self.pos = 0
        if not initial_bytes == None:
            self.buffer = str(initial_bytes)
            self.pos = len(initial_bytes)
            
    def tell(self):
        """Returns the current position"""
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
        content is returned.
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

class UnsupportedOperation(ValueError, IOError):
    pass

class StreamableArchive(object):
    """
    Base class for streamable archives using the MemoryIO class.
    """
    def __init__(self):
        self.in_memory = MemoryIO()
        self.archive = None
    
    def add_file(self, filename, bytes):
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, filename))

    def open_filestream(self, filename, filesize):
        """
        Start a file stream in the archive. An archive supporting this can add
        a file to the archive in multiple chunks.
        """
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, filename))

    def append_file_chunk(self, bytes, chunk_size):
        """
        Append a chunk of data to the currently open file stream.
        """
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, filename))

    def close_filestream(self):
        """
        Close the currently open file stream.
        """
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, filename))
    def can_write_chunks(self):
        """
        If the archive supports file streams written to the archive.
        """
        return False
    
    def read(self):
        return self.in_memory.read()

    def close(self):
        self.archive.close()


class StreamableZip(StreamableArchive):
    """
    Stream archive in ZIP format. The zip supports compression.
    """
    def __init__(self):
        super(StreamableZip, self).__init__()
        self.archive = ZipFile(self.in_memory, "w", compression=ZIP_DEFLATED)
        
    def add_file(self, filename, bytes):
         self.archive.writestr(filename, bytes)

class FileStreamException(Exception):
    pass

class StreamableTar(StreamableArchive):
    """
    Stream archive in TAR format. The archive can be compressed with
    gzip by setting archive_format to tgz or tar.gz
    """
    def __init__(self, archive_type=None):
        super(StreamableTar, self).__init__()
        mode = "w"
        if archive_type == "tgz" or archive_type == "tar.gz":
            mode += ":gz"
        self.archive = FileStreamTar.open(name=None, mode=mode, fileobj=self.in_memory)
    
    def add_file(self, filename, bytes):
        if self.archive.filestream_active:
            raise FileStreamException("Cannot add a new file with a file stream "\
                                      "currently active.")
        tarinfo = tarfile.TarInfo(filename)
        tarinfo.size = len(bytes)
        self.archive.addfile(tarinfo, MemoryIO(bytes))

    def open_filestream(self, filename, filesize):
        tarinfo = tarfile.TarInfo(filename)
        tarinfo.size = filesize
        self.archive.open_filestream(tarinfo)

    def append_file_chunk(self, bytes, chunk_size):
        self.archive.append_file_chunk(MemoryIO(bytes), chunk_size)

    def close_filestream(self):
        self.archive.close_filestream()
    
    def read(self):
        self.in_memory.seek(0)
        return super(StreamableTar, self).read()        
    
    def can_write_chunks(self):
        return True


class FileStreamTar(tarfile.TarFile):
    """
    tarfile does not directly support streaming chunks to the file.
    This class adds file streaming support to tarfile.
    """    
    def __init__(self, name=None, mode="r", fileobj=None):
        tarfile.TarFile.__init__(self, name, mode, fileobj)
        self.filestream_active = False
    
    def open_filestream(self, tarinfo):
        """Add the TarInfo object `tarinfo' to the archive and opens a filestream.
        Data chunks are appended to the filestream with append_file_chunk, and
        the filestream must be closed with close_filestream.
        """
        self._check("aw")
        if self.filestream_active:
            raise FileStreamException("Cannot start a new filestream with "\
                                      "another file stream currently active."\
                                      "Close active stream before start a new.")
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
        Appends a chunk to the current active filestream started
        with open_filestream
        """
        self._check("aw")
        if not self.filestream_active:
            raise FileStreamException("Cannot append file chunk without an "\
                                      "active filestream. Start a filestream "\
                                      "first.")
        if fileobj is None:
            raise FileStreamException("fileobj cannot be None.")

        tarfile.copyfileobj(fileobj, self.fileobj, chunk_size)
        self.offset += chunk_size
        self.filestream_sum += chunk_size
    
    def close_filestream(self):
        """
        Must be used to close a filestream session opened with open_filestream
        """
        if not self.filestream_active:
            raise FileStreamException("Cannot close a file stream when no "\
                                      "file stream is active.")
        if self.filestream_tarinfo.size != self.filestream_sum:
            raise FileStreamException("Expected size of filestream %s has not been met. "\
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
