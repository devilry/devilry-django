from django_cradmin import crinstance


class BaseCrInstanceStudent(crinstance.BaseCrAdminInstance):
    def add_extra_instance_variables_to_request(self, request):
        setattr(request, 'devilryrole', 'student')
