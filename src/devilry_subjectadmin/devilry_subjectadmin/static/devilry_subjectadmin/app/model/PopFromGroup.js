Ext.define('devilry_subjectadmin.model.PopFromGroup', {
    extend: 'Ext.data.Model',
    idProperty: 'candidate_id',
    fields: [
        {name: 'group_id', type: 'int'},
        {name: 'candidate_id', type: 'int'},
        {name: 'success', type: 'bool', persist: false},
        {name: 'new_group_id', type: 'int', persist: false}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/popfromgroup/{0}',
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
