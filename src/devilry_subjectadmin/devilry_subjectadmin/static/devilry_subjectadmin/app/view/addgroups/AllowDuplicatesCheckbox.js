Ext.define('devilry_subjectadmin.view.addgroups.AllowDuplicatesCheckbox', {
    extend: 'Ext.form.field.Checkbox',
    alias: 'widget.addgroupsallowduplicatescheckbox',
    cls: 'devilry_subjectadmin_addgroupsallowduplicatescheckbox',

    itemId: 'allowDuplicatesCheckbox',
    boxLabel: gettext('Allow duplicates'),
    tooltip: gettext('Check this to allow students to be in more than one group. Checking this stops hiding students that are already in a group on this assignment from the list. The use-case for this feature is if you have project assignments where students are in more than one project group. <strong>Keep this unchecked if you are unsure of what to do</strong>.')
});
