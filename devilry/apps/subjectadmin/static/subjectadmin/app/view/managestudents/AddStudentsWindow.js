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
     * @cfg relatedStudentsStore
     */

    initComponent: function() {
        var selModel = Ext.create('themebase.GridMultiSelectModel');
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
                html: Ext.create('Ext.XTemplate',
                    '<p>',
                    dtranslate('subjectadmin.managestudents.addstudents.tips'),
                    '</p><p>',
                    dtranslate('subjectadmin.managestudents.addstudents.relatedref'),
                    '</p>'
                ).apply({
                    period: 'stuff',
                    startlink: '<div class="relatedlink">',
                    endlink: '</div>'
                })

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
