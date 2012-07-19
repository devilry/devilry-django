/**
 * Model for the items in the array in the ``students``-attribute of
 * {@link devilry_subjectadmin.model.Group}.
 */
Ext.define('devilry_subjectadmin.model.Candidate', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'user',  type: 'auto'},
        {name: 'candidate_id',  type: 'string'}
    ]
});
