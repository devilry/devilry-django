from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
import tarfile, copy

class MemoryIO(object):
    """
    An in-memory file like IO implementation with
    read, write, seek and tell implemented.
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


class MemoryIO2(object):
    """
    An in-memory file like IO implementation with
    read, write, seek and tell implemented.
    """
    def __init__(self, initial_bytes=None):
        self.list = []
        #self.buffer = str()
        self.pos = 0
        if not initial_bytes == None:
            #self.buffer = str(initial_bytes)
            self.list.append(str(initial_bytes))
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
        content is returned. The read content is deleted from memory.
        The pos variable is deliberately not updated.
        """
        if len(self.list) == 0:
            return str()
        buf = None
        if n == -1:
            buf = str().join(self.list)
            self.list = []
        else:
            tmp = str().join(self.list)
            n = min(n, len(tmp))
            buf = tmp[:n]
            self.list = []
            self.list.append(tmp[n:])
            #self.buffer = self.buffer[n:]
        return buf

    def write(self, bytes):
        """
        Append the bytes to the in-memory buffer.
        """
        #self.buffer += str(bytes)
        self.list.append(str(bytes))
        self.pos += len(bytes)
        return len(bytes)


class UnsupportedOperation(ValueError, IOError):
    pass


class StreamableArchive(object):
    def __init__(self):
        self.in_memory = MemoryIO()
        self.archive = None
    
    def add_file(self, filename, bytes):
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, name))

    def open_filestream(self, filename, filesize):
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, name))

    def append_file_chunk(self, bytes, chunk_size):
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, name))

    def close_filestream(self):
        raise UnsupportedOperation("%s.%s() not supported" %
                                   (self.__class__.__name__, name))
    def can_write_chunks(self):
        return False
    
    def read(self):
        return self.in_memory.read()

    def close(self):
        self.archive.close()


class StreamableTar(StreamableArchive):
    def __init__(self, archive_type=None):
        super(StreamableTar, self).__init__()
        mode = "w"
        if archive_type == "tgz" or archive_type == "tar.gz":
            mode += ":gz"
        self.archive = FileStreamTar.open(name=None, mode=mode, fileobj=self.in_memory)
    
    def add_file(self, filename, bytes):
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


class StreamableZip(StreamableArchive):
    def __init__(self):
        super(StreamableZip, self).__init__()
        self.archive = ZipFile(self.in_memory, "w", compression=ZIP_DEFLATED)
        
    def add_file(self, filename, bytes):
         self.archive.writestr(filename, bytes)
        

class FileStreamTar(tarfile.TarFile):
    """
    tarfile does not directly support streaming chunks to the file.
    might be solved by letting the read method of the file-like class
    just return chunks instead of the entire file.
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
        Appends a chunk to the current active filestream started with open_filestream
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
        Must be used to close a filestream session opened with open_filestream
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
