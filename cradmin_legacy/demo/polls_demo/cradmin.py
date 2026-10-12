from cradmin_legacy import crinstance
from . import models
from .views import cradmin_question


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    roleclass = models.Question
    rolefrontpage_appname = "cradmin_questions"

    apps = [("cradmin_questions", cradmin_question.App)]

    def get_rolequeryset(self):
        return models.Question.objects.all()

    #
    # def get_titletext_for_role(self, role):
    #     return "titletext"
    #
    # def get_descriptiontext_for_role(self, role):
    #     return "descriptiontext"

    @classmethod
    def matches_urlpath(cls, urlpath):
        # Note: only here to support multiple ``BaseCrAdminInstance``s in a single django project.
        return urlpath.startswith("/polls/cradmin/")
