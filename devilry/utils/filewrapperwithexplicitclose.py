class FileWrapperWithExplicitClose(object):
    """Wrapper to convert file-like objects to iterables, with explicit close before StopIteration in next(). """

    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize

    def __getitem__(self,key):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise IndexError()

    def __iter__(self):
        return self

    def __next__(self):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        self.filelike.close()
        raise StopIteration()
