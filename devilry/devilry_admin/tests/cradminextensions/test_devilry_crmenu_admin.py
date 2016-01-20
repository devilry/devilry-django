import mock
from django import test
from model_mommy import mommy

from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin


class TestMenu(test.TestCase):
    def test_add_subject_breadcrumb_item_label(self):
        testsubject = mommy.make('core.Subject', short_name='testsubject')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'departmentadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_subject_breadcrumb_item(subject=testsubject)
        self.assertEqual('testsubject', menuitem.label)

    def test_add_subject_breadcrumb_item_include_devilryrole_departmentadmin(self):
        testsubject = mommy.make('core.Subject')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'departmentadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_subject_breadcrumb_item(subject=testsubject)
        self.assertIsNotNone(menuitem)

    def test_add_subject_breadcrumb_item_include_devilryrole_subjectadmin(self):
        testsubject = mommy.make('core.Subject')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_subject_breadcrumb_item(subject=testsubject)
        self.assertIsNotNone(menuitem)

    def test_add_subject_breadcrumb_item_exclude_devilryrole_periodadmin(self):
        testsubject = mommy.make('core.Subject')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_subject_breadcrumb_item(subject=testsubject)
        self.assertIsNone(menuitem)

    def test_add_period_breadcrumb_item_label_devilryrole_departmentadmin(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'departmentadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_period_breadcrumb_item(period=testperiod)
        self.assertEqual('testperiod', menuitem.label)

    def test_add_period_breadcrumb_item_label_devilryrole_subjectadmin(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_period_breadcrumb_item(period=testperiod)
        self.assertEqual('testperiod', menuitem.label)

    def test_add_period_breadcrumb_item_label_devilryrole_periodadmin(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_period_breadcrumb_item(period=testperiod)
        self.assertEqual('testsubject.testperiod', menuitem.label)

    def test_add_assignment_breadcrumb_item_label(self):
        testassignment = mommy.make('core.Assignment', short_name='testassignment')
        mock_cradmin_instance = mock.MagicMock()
        mock_cradmin_instance.get_devilryrole_for_requestuser.return_value = 'departmentadmin'
        menu = devilry_crmenu_admin.Menu(cradmin_instance=mock_cradmin_instance)
        menuitem = menu.add_assignment_breadcrumb_item(assignment=testassignment)
        self.assertEqual('testassignment', menuitem.label)
