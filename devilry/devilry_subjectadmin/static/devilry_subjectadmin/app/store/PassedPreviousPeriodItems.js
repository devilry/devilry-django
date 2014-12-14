Ext.define('devilry_subjectadmin.store.PassedPreviousPeriodItems', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.PassedPreviousPeriodItem',

    setAssignment: function(assignment_id) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, assignment_id);
    },

    loadGroupsInAssignment: function(assignment_id, loadConfig) {
        this.setAssignment(assignment_id);
        this.load(loadConfig);
    }
});
