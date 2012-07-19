/**
 * Model for the items in the array in the ``tags``-attribute of
 * {@link devilry_subjectadmin.model.Group}.
 */
Ext.define('devilry_subjectadmin.model.Tag', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'tag',  type: 'string'}
    ]
});
