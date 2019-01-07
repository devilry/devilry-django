class SubjectTextGenerator(object):
    """
    This class generates a subject through method `get_standard_subject`. We need
    this to generate a subject for the preferred translation of a user.
    """
    def __init__(self, **kwargs):
        pass

    def get_subject_text(self):
        raise NotImplementedError()
