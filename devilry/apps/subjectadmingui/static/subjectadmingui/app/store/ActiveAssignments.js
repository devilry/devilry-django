Ext.define('subjectadmingui.store.ActiveAssignments', {
    extend: 'Ext.data.Store',
    fields: ['id', 'short_name', 'parentnode__short_name', 'parentnode__parentnode__short_name'],
    data: [{
        id: 0,
        parentnode__parentnode__short_name:'duck1100',
        parentnode__short_name:'2012h',
        short_name:'week1'
    }, {
        id: 1,
        parentnode__parentnode__short_name:'duck1100',
        parentnode__short_name:'2012h',
        short_name:'week2'
    }, {
        id: 2,
        parentnode__parentnode__short_name:'duck-mek2030',
        parentnode__short_name:'2012h',
        short_name:'assignment1'
    }, {
        id: 3,
        parentnode__parentnode__short_name:'duck-mek2030',
        parentnode__short_name:'2012h',
        short_name:'assignment2'
    }, {
        id: 4,
        parentnode__parentnode__short_name:'duck-mek2030',
        parentnode__short_name:'2012h-extra',
        short_name:'extra'
    }]
});
