/** Groups on an assignment. */
Ext.define('devilry_subjectadmin.store.Groups', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Group',

    loadGroupsInAssignment: function(assignment_id, loadConfig) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, assignment_id);
        this.load(loadConfig);
    }
});
