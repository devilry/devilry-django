from django.views.generic import View
from django.shortcuts import render


from restful import RestfulSimplifiedDelivery


class FeedbackEditorView(View):
    def get(self, request, deliveryid):
        return render(request,
                      'examiner/feedbackeditor.django.html',
                      {'RestfulSimplifiedDelivery': RestfulSimplifiedDelivery})
