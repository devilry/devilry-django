/**
 * A window for adding students to an assignment.
 * */
Ext.define('subjectadmin.view.managestudents.AddStudentsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.addstudentswindow',
    cls: 'addstudentswindow',
    requires: [
        'themebase.SaveButton',
        'themebase.CancelButton',
        'themebase.GridMultiSelectModel'
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
        var selModel = Ext.create('themebase.GridMultiSelectModel');
        var someIgnoredTpl = Ext.create('Ext.XTemplate', dtranslate('subjectadmin.managestudents.addstudents.someignored'));
        Ext.apply(this, {
            layout: 'border',
            closable: false,
            width: 700,
            height: 500,
            maximizable: true,
            modal: true,
            title: dtranslate('subjectadmin.managestudents.addstudents.title'),
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
                            dtranslate('subjectadmin.managestudents.addstudents.allignored'),
                        '</p></tpl>',
                        '<tpl if="!allIgnored">',
                            '<p>',
                                dtranslate('subjectadmin.managestudents.addstudents.tips'),
                            '</p>',
                            '<tpl if="hasIgnored"><p>',
                                someIgnoredTpl.apply({
                                    ignoredcount: this.ignoredcount
                                }),
                            '</p></tpl>',
                            '<p>',
                                dtranslate('subjectadmin.managestudents.addstudents.onlyrelatedisavailable'),
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
                    text: dtranslate('subjectadmin.managestudents.addstudents.relatedbtn')
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
