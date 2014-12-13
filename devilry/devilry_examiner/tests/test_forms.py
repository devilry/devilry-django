from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_examiner.forms import GroupIdsForm


class TestGroupIdsForm(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')

    def test_clean_single_group(self):
        group1 = self.assignmentbuilder.add_group(examiners=[self.examiner1]).group
        formdata = {
            'group_ids': [group1.id]
        }
        form = GroupIdsForm(formdata,
            user=self.examiner1,
            assignment=self.assignmentbuilder.assignment)
        self.assertFalse(hasattr(form, 'cleaned_groups'))
        self.assertTrue(form.is_valid())
        self.assertEquals(list(form.cleaned_groups), [group1])
        self.assertEquals(list(form.cleaned_data['group_ids']), [group1.id])

    def test_clean_not_examiner(self):
        group1 = self.assignmentbuilder.add_group().group
        formdata = {
            'group_ids': [group1.id]
        }
        form = GroupIdsForm(formdata,
            user=self.examiner1,
            assignment=self.assignmentbuilder.assignment)
        self.assertFalse(form.is_valid())
        self.assertFalse(hasattr(form, 'cleaned_groups'))
        self.assertEquals(form.non_field_errors()[0],
            'One or more of the selected groups are not in duck1010.active.week1, or groups where you lack examiner permissions.')

    def test_clean_multiple_groups(self):
        group1 = self.assignmentbuilder.add_group(examiners=[self.examiner1]).group
        group2 = self.assignmentbuilder.add_group(examiners=[self.examiner1]).group
        formdata = {
            'group_ids': [group1.id, group2.id]
        }
        form = GroupIdsForm(formdata,
            user=self.examiner1,
            assignment=self.assignmentbuilder.assignment)
        self.assertFalse(hasattr(form, 'cleaned_groups'))
        self.assertTrue(form.is_valid())
        self.assertEquals(set(form.cleaned_groups), set([group1, group2]))
        self.assertEquals(set(form.cleaned_data['group_ids']), set([group1.id, group2.id]))

    def test_render_as_hiddenfields(self):
        group1 = self.assignmentbuilder.add_group(examiners=[self.examiner1]).group
        group2 = self.assignmentbuilder.add_group(examiners=[self.examiner1]).group
        formdata = {
            'group_ids': [group1.id, group2.id]
        }
        form = GroupIdsForm(formdata,
            user=self.examiner1,
            assignment=self.assignmentbuilder.assignment)
        fields = form.hidden_fields()
        self.assertEquals(len(fields), 1)
        self.assertEquals(unicode(fields[0]).count('input'), 2)
        self.assertEquals(unicode(fields[0]).count('type="hidden"'), 2)
        self.assertEquals(fields[0].name, 'group_ids')
