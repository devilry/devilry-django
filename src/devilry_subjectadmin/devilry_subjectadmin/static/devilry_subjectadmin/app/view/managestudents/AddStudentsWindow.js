/**
 * A window for adding students to an assignment.
 * */
Ext.define('devilry_subjectadmin.view.managestudents.AddStudentsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.addstudentswindow',
    cls: 'addstudentswindow',
    requires: [
        'devilry_extjsextras.SaveButton',
        'devilry_extjsextras.CancelButton',
        'devilry_extjsextras.GridMultiSelectModel'
    ],

    /**
     * @cfg {Ext.data.Store} relatedStudentsStore (required)
     */

    /**
     * @cfg {string} periodpath (required)
     */

    /**
     * @cfg {string} ignoredcount (required)
     */

    initComponent: function() {
        var selModel = Ext.create('devilry_extjsextras.GridMultiSelectModel');
        var someIgnoredTpl = Ext.create('Ext.XTemplate', gettext('<strong>{ignoredcount}</strong> students are not available in the list because they are already registered on the assignment.'));
        Ext.apply(this, {
            layout: 'border',
            closable: false,
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
                    dataIndex: 'user__devilryuserprofile__full_name',
                    menuDisabled: true,
                    flex: 1
                }, {
                    header: 'Username',
                    dataIndex: 'user__username',
                    menuDisabled: true,
                    width: 100
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
                        '<tpl if="allIgnored"><p>',
                            gettext('All students registered on <strong>{periodpath}</strong> is already added to the assignment. Use the button below to go to {periodpath} and add more students. '),
                        '</p></tpl>',
                        '<tpl if="!allIgnored">',
                            '<p>',
                                gettext('Choose the students you want to add to the assignment, and click save.'),
                            '</p>',
                            '<tpl if="hasIgnored"><p>',
                                someIgnoredTpl.apply({
                                    ignoredcount: this.ignoredcount
                                }),
                            '</p></tpl>',
                            '<p>',
                                gettext('Only students registered on <em>{periodpath}</em> is available in the list.'),
                            '</p>',
                        '</tpl>'
                    ).apply({
                        periodpath: this.periodpath,
                        hasIgnored: this.ignoredcount > 0,
                        allIgnored: this.relatedStudentsStore.getTotalCount() == this.ignoredcount
                    })
                }, {
                    xtype: 'button',
                    itemId: 'relatedLink',
                    text: gettext('Manage available students')
                }]
            }],
            buttons: ['->', {
                xtype: 'cancelbutton'
            }, {
                xtype: 'savebutton'
            }]
        });
        this.callParent(arguments);
    }
});
