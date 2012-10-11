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
                gettext('All students registered on <strong>{periodpath}</strong> is already registered on the assignment. Use the link below to go to {periodpath} and add more students.'),
            '</p>',
            '<p><strong><a target="_blank" href="{manageRelatedStudentsUrl}">',
                gettext('Add more students to {periodpath}'),
            '</a></strong> <small class="muted">(', gettext('Opens in new window') ,')</small></p>',
            '<p>',
                gettext('When you return to this page, reload it to see newly added students.'),
            '</p>'
        ).apply({
            periodpath: periodinfo.path,
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(periodinfo.id)
        });
        this.down('#help').update(help);
    }
});
