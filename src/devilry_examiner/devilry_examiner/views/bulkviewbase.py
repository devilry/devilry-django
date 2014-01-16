from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404
from devilry.apps.core.models import Assignment
from devilry_examiner.forms import GroupIdsForm



class BulkViewBase(DetailView):
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    #: The form.
    #: The primary submit button (the one that submits your form for 
    #: saving), must be named ``submit_primary``.
    #: You must also provide a ``submit_cancel`` button that can be
    #: clicked to cancel the "wizard". Clicking the cancel button takes
    #: the user to :meth:`get_cancel_url`.
    form_class = None

    groupidsform_class = GroupIdsForm

    #: Reselect the originally selected groups when redirecting back to the overview?
    #: Setting this to ``False`` deletes selected_group_ids from the session in form_valid().
    reselect_groups_on_success = True

    #: Set ``selected_group_ids`` in the session? This is required if you want back
    #: navigation to work on bulk views. If you provide an alternative single group
    #: version of the view, set this to ``False``.
    set_selected_group_ids = True

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject

    def get_success_url(self):
        return reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.object.id})

    def get_cancel_url(self):
        return self.get_success_url()

    def get_initial(self):
        """
        Get initial form data (just like Django FormView).
        """
        return {}

    def get_initial_formdata(self):
        """
        Get the initial POST data - only here to let us debug with group_ids in querystring.
        """
        if self.request.method == 'POST':
            return self.request.POST
        else:
            return self.request.GET

    def get_form_class(self):
        return self.form_class

    def get_groupidsform_class(self):
        return self.groupidsform_class

    def get(self, *args, **kwargs):
        # Redirect to POST to make it easier to debug/play with the initial post data
        return self.post(*args, **kwargs)

    def form_valid(self, form):
        if self.set_selected_group_ids \
                and 'selected_group_ids' in self.request.session \
                and not self.reselect_groups_on_success:
            del self.request.session['selected_group_ids']
        return redirect(self.get_success_url())

    def is_primary_submit(self):
        return 'submit_primary' in self.request.POST

    def groupids_form_invalid(self, groupidsform):
        raise Http404

    def post(self, *args, **kwargs):
        """
        Verfies that we get a list of at least one group_ids, and that all group_ids
        are for groups within this assignment where the requesting user is examiner.

        Expects that the name of the primary submit button of the form is ``submit_primary``.

        On the initial visit (before posting the form), we add ``group_ids_form``
        to the context, so you can get it in ``get_context_data``, or just use it
        to list the selected groups in the template like so::

            <ul>
                {% for group in group_ids_form.cleaned_groups %}
                    <li>{{ group.long_displayname }}</li>
                {% endfor %}
            </ul>

        On each request, we add ``form`` to the template context.
        """
        self.object = self.get_object()
        assignment = self.object
        self.groups = None
        common_form_kwargs = dict(assignment=assignment, user=self.request.user)

        context_data = {'object': self.object}

        form = None
        if self.is_primary_submit():
            form = self.get_form_class()(self.request.POST, **common_form_kwargs)
            if form.is_valid():
                return self.form_valid(form)
        elif 'submit_cancel' in self.request.POST:
            return redirect(self.get_cancel_url())
        else:
            # When redirected from another view like allgroupview with a list of group_ids
            # - we use a GroupIdsForm to parse the list
            groupidsform = self.get_groupidsform_class()(self.get_initial_formdata(), **common_form_kwargs)
            context_data['group_ids_form'] = groupidsform
            if groupidsform.is_valid():
                groupids = groupidsform.cleaned_data['group_ids']
                if self.set_selected_group_ids:
                    self.request.session['selected_group_ids'] = groupids
                initial = self.get_initial()
                initial['group_ids'] = groupids
                form = self.get_form_class()(
                    initial=initial,
                    **common_form_kwargs)
            else:
                self.groupids_form_invalid(groupidsform)

        # Build context just like DetailView.get, but add group_ids_form if initial load
        context_data['form'] = form
        context = self.get_context_data(**context_data)
        return self.render_to_response(context)