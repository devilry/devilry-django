from djangorestframework.resources import ModelResource
from django import forms
from django.contrib.auth.models import User

from .formfields import DevilryUserMultipleChoiceField


class BaseNodeInstanceResource(ModelResource):

    def parentnode(self, instance):
        if isinstance(instance, self.model):
            return instance.parentnode_id

    def get_form_class(self, method=None):
        queryset = User.objects.all()
        resourcemodel = self.model
        class GeneratedInstanceForm(forms.ModelForm):
            class Meta:
                model = resourcemodel
            admins = DevilryUserMultipleChoiceField(queryset=queryset, required=False)
        return GeneratedInstanceForm

    # NOTE: We may have to do something like this to allow for "id" in PUT:
    #def validate_request(self, data, files=None):
        #if 'id' in data:
            #del data['id']
        #return super(BaseNodeResource, self).validate_request(data, files)

    def can_delete(self, instance):
        if not isinstance(instance, self.model):
            return None # This happens if we do not return the instance from one of the functions (I.E.: return a dict instead)
        return instance.can_delete(self.view.user)

    def format_adminuser(self, user):
        return {
                'email': user.email,
                'username': user.username,
                'id': user.id,
                'full_name': user.devilryuserprofile.full_name
               }

    def admins(self, instance):
        if not isinstance(instance, self.model):
            return None # This happens if we do not return the instance from one of the functions (I.E.: return a dict instead)
        return [self.format_adminuser(user) for user in instance.admins.all()]
