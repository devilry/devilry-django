Ext.define('devilry_qualifiesforexam.store.Statuses', {
    extend: 'Ext.data.Store',
    model: 'devilry_qualifiesforexam.model.Status',

    loadWithinNode: function(node_id, config) {
        var actualConfig = {
            params: {
                node_id: node_id
            }
        };
        Ext.apply(actualConfig, config);
        this.load(actualConfig);
    }
});
