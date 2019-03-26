# -*- coding: utf-8 -*-


from cradmin_legacy import crinstance


class BaseDevilryCrInstance(crinstance.BaseCrAdminInstance):
    """
    Do not implement this.
    Implement one of the following subclasses::
        BaseCrInstanceAdmin
        BaseCrInstanceExaminer
        BaseCrInstanceStudent
    """
    def add_extra_instance_variables_to_request(self, request):
        setattr(request, 'devilryrole_type', self.get_devilryrole_type())

    def get_devilryrole_type(self):
        raise NotImplementedError()

    def get_devilryrole_for_requestuser(self):
        raise NotImplementedError()


class BaseCrInstanceAdmin(BaseDevilryCrInstance):
    def get_devilryrole_type(self):
        return 'admin'


class BaseCrInstanceExaminer(BaseDevilryCrInstance):
    def get_devilryrole_type(self):
        return 'examiner'

    def get_devilryrole_for_requestuser(self):
        return 'examiner'


class BaseCrInstanceStudent(BaseDevilryCrInstance):
    def get_devilryrole_type(self):
        return 'student'

    def get_devilryrole_for_requestuser(self):
        return 'student'
