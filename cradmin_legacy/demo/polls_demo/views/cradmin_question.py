from cradmin_legacy import crapp
from cradmin_legacy.viewhelpers import objecttable
from cradmin_legacy.demo.polls_demo import models
from cradmin_legacy.viewhelpers import update
from cradmin_legacy.viewhelpers import create
from cradmin_legacy.viewhelpers import delete


class QuestionTextColumn(objecttable.MultiActionColumn):
    modelfield = "question_text"

    def get_buttons(self, obj):
        return [
            objecttable.Button(label="Edit", url=self.reverse_appurl("edit", args=[obj.id])),
            objecttable.Button(label="Delete", url=self.reverse_appurl("delete", args=[obj.id]), buttonclass="danger"),
        ]


class QuestionListView(objecttable.ObjectTableView):
    model = models.Question
    columns = [QuestionTextColumn]

    def get_queryset_for_role(self, role):
        return models.Question.objects.all()


class QuestionCRUDMixin:
    model = models.Question

    def get_queryset_for_role(self, role):
        return models.Question.objects.all()


class QuestionCreateView(QuestionCRUDMixin, create.CreateView):
    """View for creating new Questions"""


class QuestionEditView(QuestionCRUDMixin, update.UpdateView):
    """View for editing Questions"""


class QuestionDeleteView(QuestionCRUDMixin, delete.DeleteView):
    """View for deleting Questions"""


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", QuestionListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"create^$", QuestionCreateView.as_view(), name="create"),
        crapp.Url(r"^edit/(?P<pk>)\d+$", QuestionEditView.as_view(), name="edit"),
        crapp.Url(r"^delete(?P<pk>)\d+$", QuestionDeleteView.as_view(), name="delete"),
    ]
