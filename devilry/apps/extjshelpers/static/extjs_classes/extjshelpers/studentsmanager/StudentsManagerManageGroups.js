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
    },

    /**
     * @private
     */
    onOneGroupForEachRelatedStudent: function() {
        this.loadAllRelatedStudents();
    },

    loadAllRelatedStudents: function() {
        var relatedStudentModel = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedRelatedStudent');

        var relatedStudentStore = Ext.create('Ext.data.Store', {
            model: relatedStudentModel,
            remoteFilter: true,
            remoteSort: true
        });

        relatedStudentStore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'period',
            comp: 'exact',
            value: this.periodid
        }]);
        //deliverystore.proxy.extraParams.orderby = Ext.JSON.encode(['-deadline__deadline', '-number']);

        relatedStudentStore.proxy.extraParams.page = 1;
        relatedStudentStore.pageSize = 1;
        relatedStudentStore.load({
            scope: this,
            callback: function(records) {
                relatedStudentStore.proxy.extraParams.page = 1;
                relatedStudentStore.pageSize = relatedStudentStore.totalCount;
                relatedStudentStore.load({
                    scope: this,
                    callback: this.onLoadAllRelatedStudents
                });
            }
        });
    },

    onLoadAllRelatedStudents: function(records) {
        console.log(records);
        console.log(records.length);
    }
});
