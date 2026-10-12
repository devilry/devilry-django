from cradmin_legacy.superuserui.views import mixins
from cradmin_legacy.viewhelpers import create


class View(mixins.QuerySetForRoleMixin, create.CreateView):
    enable_modelchoicefield_support = True
