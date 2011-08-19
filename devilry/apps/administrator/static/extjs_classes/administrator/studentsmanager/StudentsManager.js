Ext.define('devilry.administrator.studentsmanager.StudentsManager', {
    extend: 'devilry.extjshelpers.studentsmanager.StudentsManager',
    alias: 'widget.administrator_studentsmanager',

    mixins: {
        manageExaminers: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageExaminers',
        createGroups: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageGroups',
        loadRelatedUsers: 'devilry.extjshelpers.studentsmanager.LoadRelatedUsersMixin'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    }
});
