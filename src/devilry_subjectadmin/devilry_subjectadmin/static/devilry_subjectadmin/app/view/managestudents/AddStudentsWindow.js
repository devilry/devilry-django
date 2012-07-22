/**
 * A window for adding students to an assignment.
 * */
Ext.define('devilry_subjectadmin.view.managestudents.AddStudentsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.addstudentswindow',
    cls: 'addstudentswindow',
    requires: [
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.CancelButton',
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.GridMultiSelectModel',
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    /**
     * @cfg {Ext.data.Store} [relatedStudentsStore] (required)
     */

    /**
     * @cfg {Object} [periodinfo] (required)
     */

    /**
     * @cfg {int} [ignoredcount] (required)
     */

    initComponent: function() {
        var selModel = Ext.create('devilry_extjsextras.GridMultiSelectModel');
        var someIgnoredTpl = Ext.create('Ext.XTemplate',
            gettext('<strong>{ignoredcount}</strong> students are not available in the list because they are already registered on the assignment.')
        );
        Ext.apply(this, {
            layout: 'border',
            closable: true,
            width: 700,
            height: 500,
            maximizable: true,
            modal: true,
            title: gettext('Add students'),
            items: [{
                xtype: 'grid',
                region: 'center',
                store: this.relatedStudentsStore,
                selModel: selModel,
                columns: [{
                    header: 'Name',
                    dataIndex: 'id',
                    menuDisabled: true,
                    flex: 1,
                    renderer: function(unused1, unused2, relatedStudentRecord) {
                        return relatedStudentRecord.get('user').full_name;
                    }
                }, {
                    header: 'Username',
                    dataIndex: 'id',
                    menuDisabled: true,
                    width: 100,
                    renderer: function(unused1, unused2, relatedStudentRecord) {
                        return relatedStudentRecord.get('user').username;
                    }
                }],
            }, {
                xtype: 'panel',
                region: 'east',
                width: 250,
                bodyPadding: 20,
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: Ext.create('Ext.XTemplate',
                        '<tpl if="allIgnored">',
                            '<p>',
                                gettext('All students registered on <strong>{periodpath}</strong> is already added to the assignment. Use the link below to go to {periodpath} and add more students.'),
                            '</p>',
                        '<tpl else>',
                            '<p>',
                                gettext('Choose the students you want to add to the assignment, and click {savebuttonlabel}.'),
                            '</p>',
                            '<tpl if="hasIgnored"><p>',
                                someIgnoredTpl.apply({
                                    ignoredcount: this.ignoredcount
                                }),
                            '</p></tpl>',
                            '<p>',
                                gettext('Only students registered on <em>{periodpath}</em> is available in the list.'),
                            '</p>',
                        '</tpl>',
                        '<p><a target="_blank" href="{manageRelatedStudentsUrl}">',
                            gettext('Add more students to {periodpath}'),
                        '</a></p>'
                    ).apply({
                        periodpath: this.periodinfo.path,
                        hasIgnored: this.ignoredcount > 0,
                        manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.periodinfo.id),
                        savebuttonlabel: gettext('Add students'),
                        allIgnored: this.relatedStudentsStore.getTotalCount() == this.ignoredcount
                    })
                }]
            }],
            buttons: ['->', {
                //xtype: 'cancelbutton'
            //}, {
                xtype: 'primarybutton',
                text: gettext('Add students')
            }]
        });
        this.callParent(arguments);
    }
});
