from django import urls
from django.utils.translation import gettext_lazy
from django.views.generic import edit
from django.views.generic import base
from django import forms
from django.core import exceptions

from crispy_forms import helper
from crispy_forms import layout
import json

from devilry.devilry_bulkcreate_users import create_users


class EmailListForm(forms.Form):
    email_list = forms.CharField(label=gettext_lazy("New user e-mails"), required=True, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(EmailListForm, self).__init__(*args, **kwargs)
        self.helper = helper.FormHelper(self)
        self.helper.form_action = ""
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                gettext_lazy('Enter list of e-mails for new users'),
                'email_list'
            ),
            layout.Div(
                layout.Submit('submit', gettext_lazy('Submit'), css_class='btn btn-primary')
            )
        )

    def validate_userdata(self):
        bulkcreator = create_users.BulkCreateUsers()
        bulkcreator.add_userdata(self.cleaned_data['email_list'])
        return {'valid': bulkcreator.get_userdata(), 'conflicting': bulkcreator.get_conflicting_users()}


class IsSuperuserPermissionMixin(object):
    """
    Simple mixin class for all views in this module
    ensures that only superusers can use the bulk-creation views.

    TODO: There is probably something like this class somewhere else, that should rather be used?
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied("This view is only available for superusers")

        return super(IsSuperuserPermissionMixin, self).dispatch(request, *args, **kwargs)


class SubmitUsers(IsSuperuserPermissionMixin, edit.FormView):
    """
    Displays a form for adding a list of usernames or emails, in order to create users in bulk.

    This class will only perform validation (via :class:`devilry.devilry_bulkcreate_users.create_users.BulkCreateUsers`)

    The validated result will be displayed and stored in other views.
    """
    form_class = EmailListForm
    template_name = 'devilry_bulkcreate_users/submit_bulkcreate_users.django.html'

    def __init__(self):
        super(SubmitUsers, self).__init__()
        self.conflicting_users = []
        self.valid_users = []

    def form_valid(self, form):
        """
        validate usernames/emails from input, and stores result in instance-variables

        :param form: the submitted form from ui
        :return: result from superclass
        """
        status = form.validate_userdata()
        self.conflicting_users = status['conflicting']
        self.valid_users = status['valid']
        return super(SubmitUsers, self).form_valid(form)

    def get_form(self, form_class):
        """
        Add form_action to form, and return
        """
        form = super(SubmitUsers, self).get_form(form_class)
        form.helper.form_action = self.request.path
        return form

    def get_success_url(self):
        """
        :return: url to `confirm_bulkcreated_users` with json dump of valid and conflicting users from validation
        """
        return '{}?valid_users={}&conflicting_users={}'.format(
                urls.reverse('confirm_bulkcreated_users'),
                json.dumps(self.valid_users), json.dumps(self.conflicting_users))


class ConfirmUsers(IsSuperuserPermissionMixin, base.TemplateView):
    """
    Display results from validation performed in :class:`SubmitUsers`, and allow current user
    to confirm bulkcreation
    """
    template_name = 'devilry_bulkcreate_users/confirm_bulkcreated_users.django.html'

    def get_context_data(self, **kwargs):
        """
        fetch json-encoded validationresult from queryparams and pass them along to the view
        """
        context = super(ConfirmUsers, self).get_context_data(**kwargs)
        json_valid_users = self.request.GET.get('valid_users', {})
        valid_users = json.loads(json_valid_users)
        conflicting_users = json.loads(self.request.GET.get('conflicting_users', {}))
        context['valid_users'] = valid_users
        context['conflicting_users'] = conflicting_users
        context['confirmation_url'] = urls.reverse('save_bulkcreated_users', kwargs={'userdata': json_valid_users})
        context['cancel_url'] = urls.reverse('bulkcreate_users_by_email')
        print(context)
        return context


class SaveConfirmedUsers(IsSuperuserPermissionMixin, base.RedirectView):
    """
    Save validated and confirmed userdata as new :class:`User`\s, then redirect to :class:`DisplayCreatedUsers`
    """
    permanent = True
    query_string = True
    pattern_name = 'display_bulkcreated_users'

    def __save_users(self, userdata):
        """
        use the :class:`BulkCreateUsers` to save all users in `userdata`

        :param userdata: parsed, validated userdata.
        """
        bulkcreator = create_users.BulkCreateUsers()
        bulkcreator.add_userdata(userdata, parse_data=False)
        bulkcreator.create_users()

        created_users = {}
        for user in bulkcreator.get_created_users():
            created_users[user.username] = user.email
        return created_users

    def get_redirect_url(self, *args, **kwargs):
        """
        Load userdata from kwargs and save the users (using `__save_users`)
        """
        userdata = json.loads(kwargs.get('userdata', "{}"))
        del(kwargs['userdata'])

        created_users = json.dumps(self.__save_users(userdata))
        kwargs['created_users'] = created_users
        return super(SaveConfirmedUsers, self).get_redirect_url(*args, **kwargs)


class DisplayCreatedUsers(IsSuperuserPermissionMixin, base.TemplateView):
    """
    Display list of newly created :class:`User`\s
    """
    template_name = 'devilry_bulkcreate_users/show_bulkcreated_users.django.html'

    def get_context_data(self, **kwargs):
        """
        load created users from `kwargs` and present them in template (via context).
        """
        context = super(DisplayCreatedUsers, self).get_context_data(**kwargs)
        context['created_users'] = json.loads(kwargs.get('created_users', "[]"))
        return context