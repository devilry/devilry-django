/**
 * Group-model for the ``/subjectadmin/rest/group`` API.
 */
Ext.define('devilry_subjectadmin.model.Group', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'num_deliveries', type: 'int'},
        {name: 'name',  type: 'string'},
        {name: 'is_open',  type: 'boolean'},
        {name: 'tags', type: 'auto'},
        {name: 'feedback',  type: 'auto'},
        {name: 'candidates', type: 'auto'},
        {name: 'examiners', type: 'auto'},
        {name: 'deadlines', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/group/{0}',
        url: null, // We use urlpatt to dynamically generate the url
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    _debugFormatArray: function(array, tpl) {
        var itemtpl = Ext.create('Ext.XTemplate', tpl);
        var items = [];
        Ext.Array.each(array, function(item, index) {
            items.push('\n    ' + index + ': {' + itemtpl.apply(item) + '}');
        }, this);
        return items.join(', ');
    },

    debugFormat: function() {
        var usertpl = [
            'id:{id}, ',
            '<tpl if="candidate_id">candidate_id:{candidate_id}, </tpl>',
            'user.id:{user.id}, username:{user.username}, full_name:{user.full_name}, email:{user.email}'
        ];
        var tagtpl = ['id:{id}, tag:{tag}'];
        return Ext.String.format('id={0}, num_deliveries={1}, name={2}, is_open={3},\n- tags=[{4}],\n- candidates=[{5}],\n- examiners=[{6}]',
            this.get('id'),
            this.get('num_deliveries'),
            this.get('name'),
            this.get('is_open'),
            this._debugFormatArray(this.get('tags'), tagtpl),
            this._debugFormatArray(this.get('candidates'), usertpl),
            this._debugFormatArray(this.get('examiners'), usertpl)
        );
    }
});
