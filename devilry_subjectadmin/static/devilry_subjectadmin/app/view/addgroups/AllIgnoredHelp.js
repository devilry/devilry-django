Ext.define('devilry_subjectadmin.view.addgroups.AllIgnoredHelp', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.addgroupsallignored',
    cls: 'devilry_subjectadmin_addgroupsallignoredhelp bootstrap',

    requires: [
        'Ext.form.FieldSet'
    ],

    bodyPadding: 40,
    items: [{
        xtype: 'box',
        itemId: 'help'
    }, {
        xtype: 'fieldset',
        margin: '20 0 0 0',
        collapsible: true,
        collapsed: true,
        title: gettext('Advanced options'),
        items: [{
            xtype: 'box',
            cls: 'bootstrap',
            html: [
                '<h2>', gettext('Allow duplicates?'), '</h2>',
                '<p>',
                    gettext('If you want to add the same student to more than one group on this assignment, click the button below. The use-case for this feature is if you have project assignments where students are in more than one project group. <strong>Keep this unchecked if you are unsure of what to do</strong>.'),
                '</p>'
            ].join('')
        }, {
            xtype: 'button',
            itemId: 'allowDuplicatesButton',
            text: 'Allow duplicates'
        }]
    }],

    setBody: function(periodinfo, totalStudentsOnPeriod) {
        var help = Ext.create('Ext.XTemplate',
            '<h1>', gettext('No students available') ,'</h1>',
            '<tpl if="periodHasStudents">',
                '<p>',
                    gettext('All students registered on {periodpath} is already registered on the assignment.'),
                '</p>',
            '<tpl else>',
                '<p class="text-warning no_students_on_period_warning">',
                    gettext('There is no students on {periodpath}. Only students registered on {periodpath} can be added to this assignment.'),
                '</p>',
            '</tpl>',
            '<tpl if="isPeriodadmin">',
                '<p><strong><a target="_blank" href="{manageRelatedStudentsUrl}" class="add_more_students_to_period_link new-window-link">',
                    gettext('Add students to {periodpath}'),
                '</a></strong></p>',
                '<p>',
                    gettext('When you return to this page, reload it to see newly added students.'),
                '</p>',
            '<tpl else>',
                '<p class="text-warning not_periodadmin_warning">',
                    gettext('You do not have administrator rights on {periodpath}, so you need to ask someone with administrator rights if you need to add more students.'),
                '</p>',
            '</tpl>'
        ).apply({
            periodpath: periodinfo.path,
            periodHasStudents: totalStudentsOnPeriod > 0,
            isPeriodadmin: periodinfo.is_admin,
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(periodinfo.id)
        });
        this.down('#help').update(help);
    }
});
