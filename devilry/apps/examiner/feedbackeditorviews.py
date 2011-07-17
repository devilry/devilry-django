from django.views.generic import View
from django.shortcuts import render


from restful import RestfulSimplifiedDelivery, RestfulSimplifiedFileMeta


class FeedbackEditorView(View):
    def get(self, request, deliveryid):
        return render(request,
                      'examiner/feedbackeditor.django.html',
                      {'RestfulSimplifiedDelivery': RestfulSimplifiedDelivery,
                       'RestfulSimplifiedFileMeta': RestfulSimplifiedFileMeta,
                       'deliveryid': deliveryid})
