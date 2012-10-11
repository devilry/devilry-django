Ext.define('devilry_subjectadmin.view.addgroups.AllIgnoredHelp', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.addgroupsallignored',
    cls: 'devilry_subjectadmin_addgroupsallignoredhelp bootstrap',

    bodyPadding: 40,
    items: [{
        xtype: 'box',
        itemId: 'help'
    }],
    tbar: [{
        text: gettext('Advanced options'),
        menu: {
            xtype: 'menu',
            plain: true,
            items: [{
                xtype: 'addgroupsallowduplicatescheckbox'
            }]
        }
    }],

    setBody: function(periodinfo) {
        var help = Ext.create('Ext.XTemplate',
            '<p>',
                gettext('All students registered on {periodpath} is already registered on the assignment.'),
            '</p>',
            '<tpl if="is_periodadmin">',
                '<p><strong><a target="_blank" href="{manageRelatedStudentsUrl}">',
                    gettext('Add more students to {periodpath}'),
                '</a></strong> <small class="muted">(', gettext('Opens in new window') ,')</small></p>',
                '<p>',
                    gettext('When you return to this page, reload it to see newly added students.'),
                '</p>',
            '<tpl else>',
                '<p class="text-warning">',
                    gettext('You do not have administrator rights on {periodpath}, so you need to ask someone with administrator rights if you need to add more students.'),
                '</p>',
            '</tpl>'
        ).apply({
            periodpath: Ext.String.format('<em>{0}</em>', periodinfo.path),
            is_periodadmin: periodinfo.is_admin,
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(periodinfo.id)
        });
        this.down('#help').update(help);
    }
});
