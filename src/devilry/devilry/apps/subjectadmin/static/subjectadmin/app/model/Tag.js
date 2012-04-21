/**
 * Model for the items in the array in the ``tags``-attribute of
 * {@link subjectadmin.model.Group}.
 */
Ext.define('subjectadmin.model.Tag', {
    extend: 'Ext.data.Model',
    idProperty: 'tag',
    fields: [
        {name: 'tag',  type: 'string'}
    ]
});
