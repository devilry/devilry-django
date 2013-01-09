Ext.define('devilry_qualifiesforexam.model.AggregatedRelatedStudentInfo', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'auto', pesist: false},
        {name: 'user',  type: 'auto', pesist: false},
        {name: 'groups_by_assignment',  type: 'auto', pesist: false},
        {name: 'relatedstudent',  type: 'auto', pesist: false}
    ]
});
