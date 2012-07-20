/** Selected groups in managestudents. */
Ext.define('devilry_subjectadmin.store.SelectedGroups', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Group',
    proxy: 'memory'
});
