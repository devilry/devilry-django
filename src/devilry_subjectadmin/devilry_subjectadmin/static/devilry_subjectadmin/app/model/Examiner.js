/**
 * Model for the items in the array in the ``examiner``-attribute of
 * {@link devilry_subjectadmin.model.Group}.
 */
Ext.define('devilry_subjectadmin.model.Examiner', {
    extend: 'Ext.data.Model',
    idProperty: 'user__username',
    fields: [
        {name: 'user__username',  type: 'string'},
        {name: 'user__devilryuserprofile__full_name',  type: 'string'},
        {name: 'user__email',  type: 'string'}
    ]
});
