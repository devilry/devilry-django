Ext.define('devilry_subjectadmin.view.assignment.GradeEditorSelectWidget', {
    extend: 'devilry_extjsextras.EditableSidebarBox',
    alias: 'widget.gradeeditorselect-widget',
    cls: 'devilry_gradeeditorselect_widget',
    title: gettext('Grade editor'),
    bodyTpl: [
        '<p>',
            '<tpl if="text">',
                '<small>{text}</small>',
            '<tpl else>',
                '<tpl if="isMissingConfig">',
                    '<p class="danger">',
                        gettext('Missing grade editor config.'),
                    '</p>',
                    '<p><a href="#">',
                        gettext('Configure grade editor'),
                    '</a></p>',
                '<tpl else>',
                    '<small>{description}</small>',
                '</tpl>',
            '</tpl>',
        '</p>'
    ]
});
