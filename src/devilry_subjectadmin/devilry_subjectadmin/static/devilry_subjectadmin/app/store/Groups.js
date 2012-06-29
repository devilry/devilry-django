/** Groups on an assignment. */
Ext.define('devilry_subjectadmin.store.Groups', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Group',

    loadGroupsInAssignment: function(assignment_id, callbackFn, callbackScope) {
        var url = Ext.String.format('{0}{1}/', this.proxy.baseurl, assignment_id);
        this.proxy.url = url;
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    }
});
