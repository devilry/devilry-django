from .models import SubsetPluginSetting


def save_subset_settings(status, settings):
    assignmentids_that_must_be_passed = settings['assignmentids_that_must_be_passed']
    subset = SubsetPluginSetting.objects.create(status=status)
    for assignmentid in assignmentids_that_must_be_passed:
        subset.selectedassignment_set.create(assignment_id=assignmentid)