Ext.define('devilry_subjectadmin.model.MergeIntoGroup', {
    extend: 'Ext.data.Model',
    idProperty: 'target_group_id',
    fields: [
        {name: 'source_group_ids', type: 'auto'},
        {name: 'target_group_id', type: 'int'},
        {name: 'success', type: 'bool', persist: false}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/mergeintogroup/{0}',
        url: null, // We use urlpatt to dynamically generate the url
        appendId: false, 
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        },
        setUrl: function(assignment_id) {
            this.url = Ext.String.format(this.urlpatt, assignment_id);
        }
    }
});
