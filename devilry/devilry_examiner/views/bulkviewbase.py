from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404
from django import forms

from devilry.apps.core.models import Assignment
from devilry.devilry_examiner.forms import GroupIdsForm


class OptionsForm(GroupIdsForm):
    success_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput())
    cancel_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput())



class BulkViewBase(DetailView):
    """
    Handles the bulk action on selected groups workflow.

    How it works
    ============
    We only allow POST requests.
    
    Options form
    ------------
    We define an options form that is validated on the first POST. This form
    should inherit from :class:`.OptionsForm`, which validates the ID of the
    selected groups.

    Primary forms
    -------------
    We also define one or more primary forms. A primary form is a form that the user
    interracts with. Lets use the bulk create feedback preview view as an example. In this
    view, we create two primary forms:

    1. The form wrapping the publish button. This form has the view as POST url and the group
       IDs and any other options (first given in the options form), in hidden fields.
    2. The form wrapping the edit draft button. This form has the edit draft view as the
       POST url and the group IDs and any other options (first given in the options form),
       in hidden fields.

    As we can see, the common feature of the forms is that they forward the data first given
    in the options form. Handling this is easy:

    1. Make sure all primary forms inherit from the options form.
    2. Make sure to initialize all primary forms with ``request.POST`` as input.
       We handle this automatically.
    3. Only validate the submitted form.
       We handle this automatically.
    """
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    #: We only allow POST requests
    http_method_names = ['post']

    #: The form used to parse initial options.
    optionsform_class = OptionsForm

    #: Dictionary mapping submit button name to primary form class.
    primaryform_classes = {}

    #: Reselect the originally selected groups when redirecting back to the overview?
    #: Setting this to ``False`` deletes selected_group_ids from the session in submitted_primaryform_valid().
    reselect_groups_on_success = True

    #: Set ``selected_group_ids`` in the session? This is required if you want back
    #: navigation to work on bulk views. If you provide an alternative single group
    #: version of the view, set this to ``False``.
    set_selected_group_ids = True


    def get_queryset(self):
        """
        Should not have to override this, but it may be useful to override it
        to add extra ``select_related`` or ``prefetch_related``.
        """
        return Assignment.objects.filter_examiner_has_access(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject

    def get_success_url(self):
        if self.optionsdict['success_url']:
            return self.optionsdict['success_url']
        else:
            return reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.object.id})

    def get_cancel_url(self):
        if self.optionsdict['cancel_url']:
            return self.optionsdict['cancel_url']
        else:
            return self.get_success_url()


    @property
    def optionsdict(self):
        """
        Get the cleaned data from the options form.

        This is available in all of the ``*_valid`` and ``*_invalid`` methods
        except ``optionsform_invalid``. When it is not available, it raises
        AttributeError.

        Available in the template context under the same name.
        """
        return self.__optionsform.cleaned_data
    
    @property
    def selected_groups(self):
        """
        Get the QuerySet for the selected groups.

        Available just like :class:`.optionsdict`.
        """
        return self.__optionsform.cleaned_groups
    


    #
    #
    # Options form
    #
    #

    def optionsform_invalid(self, optionsform):
        """
        Called if the options for is not valid. Should raise an exception,
        or return a HttpResponse. Defaults to raising the django.http.Http404
        exception.
        """
        raise Http404

    def get_optionsform_class(self):
        return self.optionsform_class

    def optionsform_valid(self, context_data):
        """
        Called on the first POST request if the options form is valid.

        The ``context_data`` will contain the following data:

            primaryforms
                Dict of all primary forms returned by :meth:`.get_primaryform_classes`
                initialized with :meth:`.get_primaryform_initial_data`. The key 
                is the submit button name from get_primaryform_classes.

        Defaults to calling :meth:`.render_view` with the given ``context_data``.
        """
        return self.render_view(context_data)

    #
    #
    # Primary forms
    #
    #

    def get_primaryform_classes(self):
        """
        Return a dict mapping submit button name to form class.

        ALL forms MUST inherit from :obj:`.optionsform_class`.
        """
        return self.primaryform_classes

    def get_primaryform_initial_data(self, formclass):
        """
        Get initial form data for the given primary ``formclass`` (just like Django FormView.get_initial()).
        """
        return self.optionsdict.copy()

    def submitted_primaryform_valid(self, form, context_data):
        """
        Called when the submitted primary form is valid. If you need special Handling
        for each primary form, use ``isintance(form, MyFormClass)``.

        The default action is to redirect to the success url.
        """
        # if self.set_selected_group_ids \
        #         and 'selected_group_ids' in self.request.session \
        #         and not self.reselect_groups_on_success:
        #     del self.request.session['selected_group_ids']
        return redirect(self.get_success_url())

    def submitted_primaryform_invalid(self, form, context_data):
        """
        Called when the submitted primaryform is invalid. ``context_data``
        will contain the same data as it does in :meth:`.optionsform_valid`.
        """
        return self.render_view(context_data)


    #
    #
    # Handle POST requests - should not have to override any of these methods
    #
    #

    def get_common_form_kwargs(self):
        return dict(assignment=self.assignment, user=self.request.user)

    def _initialize_primaryforms(self):
        forms = {}
        submitted_primaryform = None
        for submitname, formclass in self.get_primaryform_classes().iteritems():
            submitted = submitname in self.request.POST
            if submitted:
                form = formclass(self.request.POST, **self.get_common_form_kwargs())
                submitted_primaryform = form
            else:
                form = formclass(initial=self.get_primaryform_initial_data(formclass),
                    **self.get_common_form_kwargs())
            forms[submitname] = form
        return forms, submitted_primaryform

    def post(self, *args, **kwargs):
        """
        Routes POST requests to methods that can be overridden in subclasses:

        - Validate :meth:`.get_optionsform_class`.
        - If the options for is valid:
            - If ``submit_cancel`` in POST, redirect to :meth:`.get_cancel_url`.
            - Else:
                - If one of the keys in :meth:`.get_primaryform_classes` is in POST
                    - Validate the submitted form.
                    - If the submitted form is valid:
                        - Return :meth:`.submitted_primaryform_valid`
                    - Else:
                        - Return :meth:`.submitted_primaryform_invalid`
                - Else:
                    - Return :meth:`.optionsform_valid`.
        - If the options for is NOT valid:
            - Return :meth:`.optionsform_invalid`.
        """
        self.object = self.get_object()
        self.assignment = self.object

        # NOTE: We ALWAYS validate the options form, to ensure all forms inherit
        #       from it, and to ensure we always have the options available.
        optionsform = self.get_optionsform_class()(self.request.POST, **self.get_common_form_kwargs())
        if optionsform.is_valid():
            self.__optionsform = optionsform
            if 'submit_cancel' in self.request.POST:
                return redirect(self.get_cancel_url())
            else:
                context_data = {}
                forms, submitted_primaryform = self._initialize_primaryforms()
                context_data['primaryforms'] = forms
                if submitted_primaryform:
                    context_data['submitted_primaryform'] = submitted_primaryform
                    if submitted_primaryform.is_valid():
                        return self.submitted_primaryform_valid(submitted_primaryform, context_data)
                    else:
                        return self.submitted_primaryform_invalid(submitted_primaryform, context_data)
                else:
                    return self.optionsform_valid(context_data)
        else:
            return self.optionsform_invalid(optionsform)


    def render_view(self, context_data):
        """
        Render the template with the given ``context_data``. Calls
        ``self.get_context_data(**context_data)``, so you should
        override ``get_context_data`` instead of this method to
        add template variables.

        Should not have to override this method, but you will
        probably want to call it from some of your ``_valid(...)``
        and ``_invalid(...)`` methods.
        """
        context = self.get_context_data(**context_data)
        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(BulkViewBase, self).get_context_data(**kwargs)
        try:
            context['optionsdict'] = self.optionsdict
            context['selected_groups'] = self.selected_groups
        except AttributeError:
            pass
        return context
