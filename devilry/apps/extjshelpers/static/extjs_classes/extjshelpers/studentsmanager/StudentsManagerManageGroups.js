/** The group management methods for StudentsManager. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerManageGroups', {

    /**
     * @private
     */
    onManuallyCreateUsers: function() {
        var win = Ext.widget('window', {
            title: 'Create assignment groups',
            modal: true,
            width: 830,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'manuallycreateusers',
                assignmentid: this.assignmentid
            },
            listeners: {
                scope: this,
                close: function() {
                    this.refreshStore();
                }
            }
        });
        win.show();
    }
});
