/** The group management methods for StudentsManager. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageGroups', {
    requires: [
        'devilry.administrator.studentsmanager.ManuallyCreateUsers'
    ],

    /**
     * @private
     */
    showManuallyCreateUsersWindow: function(initialLines) {
        var win = Ext.widget('window', {
            title: 'Create assignment groups',
            modal: true,
            width: 830,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'manuallycreateusers',
                deadlinemodel: this.deadlinemodel,
                assignmentid: this.assignmentid,
                initialLines: initialLines
            },
            listeners: {
                scope: this,
                close: function() {
                    this.refreshStore();
                }
            }
        });
        win.show();
    },

    /**
     * @private
     */
    onManuallyCreateUsers: function() {
        this.showManuallyCreateUsersWindow();
    },

    /**
     * @private
     */
    onOneGroupForEachRelatedStudent: function() {
        this.loadAllRelatedStudents({
            scope: this,
            callback: this.createOneGroupForEachRelatedStudent
            //args: ['Hello world']
        });
    },

    /**
     * @private
     */
    createOneGroupForEachRelatedStudent: function(relatedStudents) {
        this.showManuallyCreateUsersWindow(this.relatedUserRecordsToArray(relatedStudents));
    }
});
