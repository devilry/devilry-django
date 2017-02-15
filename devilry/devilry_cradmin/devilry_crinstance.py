# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crinstance


class BaseDevilryCrInstance(crinstance.BaseCrAdminInstance):
    """
    Do not implement this.
    Implement one of the following subclasses::
        BaseCrInstanceAdmin
        BaseCrInstanceExaminer
        BaseCrInstanceStudent
    """
    def add_extra_instance_variables_to_request(self, request):
        raise NotImplementedError()

    def get_devilryrole_for_requestuser(self):
        raise NotImplementedError()


class BaseCrInstanceAdmin(BaseDevilryCrInstance):
    def add_extra_instance_variables_to_request(self, request):
        setattr(request, 'devilryrole_type', 'admin')


class BaseCrInstanceExaminer(BaseDevilryCrInstance):
    def add_extra_instance_variables_to_request(self, request):
        setattr(request, 'devilryrole_type', 'examiner')

    def get_devilryrole_for_requestuser(self):
        return 'examiner'


class BaseCrInstanceStudent(BaseDevilryCrInstance):
    def add_extra_instance_variables_to_request(self, request):
        setattr(request, 'devilryrole_type', 'student')

    def get_devilryrole_for_requestuser(self):
        return 'student'
