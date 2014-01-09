from devilry.apps.core.models import Delivery


# from django.core.urlresolvers import reverse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required




class FeedbackEditorSingleDeliveryObjectMixin(SingleObjectMixin):
    """
    Mixin that provides:

    - A delivery object.
    - Authorization for access to the delivery object.

    If your are creating a grading system plugin, you should NOT USE THIS
    directly. Use :class:`.FeedbackEditorBaseView` instead. 
    """
    model = Delivery
    pk_url_kwarg = 'deliveryid'
    context_object_name = 'delivery'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackEditorBaseView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Ensure we only match deliveries where the current user has access
        as an examiner.
        """
        return Delivery.objects.filter_examiner_has_access(self.request.user)\
            .select_related( # Use select_related to lookup all the related objects in the query
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode', # Assignment
                'deadline__assignment_group__parentnode__parentnode', # Period
                'deadline__assignment_group__parentnode__parentnode__parentnode') # Subject



class FeedbackEditorBaseView(FeedbackEditorSingleDeliveryObjectMixin, FormView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(FeedbackEditorBaseView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('devilry_examiner_singledeliveryview', kwargs={'deliveryid': self.object.id})