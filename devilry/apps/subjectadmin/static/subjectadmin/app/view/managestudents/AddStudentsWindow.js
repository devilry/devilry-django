/**
 * A window for adding students to an assignment.
 * */
Ext.define('subjectadmin.view.managestudents.AddStudentsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.addstudentswindow',
    cls: 'addstudentswindow',
    requires: [
        'themebase.SaveButton',
        'themebase.CancelButton'
    ],

    /**
     * @cfg relatedStudentsStore
     */

    initComponent: function() {
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
                html: dtranslate('subjectadmin.managestudents.addstudents.tips')
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
