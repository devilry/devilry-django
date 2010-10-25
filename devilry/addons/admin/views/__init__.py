from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from devilry.core.models import Node, Subject, Period, Assignment, \
        AssignmentGroup
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryLongNameWidget
from devilry.ui.fields import MultiSelectCharField

from shortcuts import EditBase, deletemany_generic, admins_help_text
from assignment import edit_assignment



@login_required
def delete_manyassignmentgroups(request, assignment_id):
    return deletemany_generic(request, AssignmentGroup,
            successurl=reverse('devilry-admin-edit_assignment',
                args=[assignment_id]))


