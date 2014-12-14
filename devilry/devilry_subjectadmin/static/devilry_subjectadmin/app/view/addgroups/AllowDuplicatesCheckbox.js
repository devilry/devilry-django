Ext.define('devilry_subjectadmin.view.addgroups.AllowDuplicatesCheckbox', {
    extend: 'Ext.form.field.Checkbox',
    alias: 'widget.addgroupsallowduplicatescheckbox',
    cls: 'devilry_subjectadmin_addgroupsallowduplicatescheckbox',

    itemId: 'allowDuplicatesCheckbox',
    boxLabel: gettext('Allow duplicates'),
    tooltip: gettext('Uncheck this to hide any students already in a group from the list below.')
});
