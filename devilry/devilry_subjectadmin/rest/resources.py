from django import forms
from django.contrib.auth.models import User
from django.forms.fields import DateTimeField

from djangorestframework.resources import ModelResource
from devilry.devilry_subjectadmin.rest.fields import DevilryUserMultipleChoiceField


_admins_helptext = """
List of maps(dict/hashmap/object). Each map contains the following attributes:

- ``id`` (unique user-id). Eighter ``id`` or ``username`` must be supplied. ``id`` is preferred.
- ``username`` (unique user-id). Eighter ``id`` or ``username`` must be supplied. ``username`` is ignored  if ``id`` is supplied.
- ``email`` (ignored, but including it does not raise an error).
- ``full_name`` (ignored, but including it does not raise an error).
"""

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
            admins = DevilryUserMultipleChoiceField(queryset=queryset, required=False,
                                                    help_text=_admins_helptext)
        return GeneratedInstanceForm

    # NOTE: We may have to do something like this to allow for "id" in PUT:
    #def validate_request(self, data, files=None):
        #if 'id' in data:
            #del data['id']
        #return super(BaseNodeInstanceResource, self).validate_request(data, files)

    def validate_request(self, data, files=None):
        form = self.view.get_bound_form()
        for fieldname in data.keys():
            if not fieldname in form.fields:
                del data[fieldname]
            else:
                field = form.fields[fieldname]
                value = data[fieldname]
                if value and isinstance(field, DateTimeField):
                    if 'T' in value:
                        data[fieldname] = value.replace('T', ' ')
        return super(BaseNodeInstanceResource, self).validate_request(data, files)

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

    def _get_typename(self, basenode):
        return basenode.__class__.__name__

    def format_inheritedadmin(self, inheritedadmin):
        return {'user': self.format_adminuser(inheritedadmin.user),
                'basenode': {'type': self._get_typename(inheritedadmin.basenode),
                             'is_admin': inheritedadmin.basenode.is_admin(self.view.request.user),
                             'path': inheritedadmin.basenode.get_path(),
                             'id': inheritedadmin.basenode.id}}

    def admins(self, instance):
        if not isinstance(instance, self.model):
            return None # This happens if we do not return the instance from one of the functions (I.E.: return a dict instead)
        return [self.format_adminuser(user)
                for user in instance.admins.all().prefetch_related('devilryuserprofile')]

    def inherited_admins(self, instance):
        if isinstance(instance, self.model):
            return [self.format_inheritedadmin(inheritedadmin)
                    for inheritedadmin in instance.get_inherited_admins()]

    def _add_breadcrumbitem(self, breadcrumb, basenode):
        if basenode.parentnode and basenode.parentnode.can_save(self.view.user):
            text = basenode.short_name
            self._add_breadcrumbitem(breadcrumb, basenode.parentnode) # Add parent before self to get reversed result
        else:
            text = basenode.get_path()
        breadcrumb.append({'id': basenode.id,
                           'type': self._get_typename(basenode),
                           'text': text})

    def breadcrumb(self, instance):
        if isinstance(instance, self.model):
            breadcrumb = []
            self._add_breadcrumbitem(breadcrumb, instance)
            return breadcrumb
