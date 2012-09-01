Ext.define('devilry_subjectadmin.view.assignment.GradeEditorSelectWidget', {
    extend: 'devilry_extjsextras.EditableSidebarBox',
    alias: 'widget.gradeeditorselect-widget',
    cls: 'devilry_subjectadmin_gradeeditorselect_widget',
    title: gettext('Grade editor'),
    bodyTpl: [
        '<tpl if="text">',
            '<p><small>{text}</small></p>',
        '<tpl else>',
            '<p class="muted">{title}</p>',
            '<tpl if="isMissingConfig">',
                '<div class="alert alert-error">',
                    gettext('Missing grade editor config. You have to configure this grade editor before any feeback may be provided on this assignment.'),
                '</div>',
            '</tpl>',
        '</tpl>'
    ]
});
