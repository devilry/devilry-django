Ext.define('subjectadmin.store.ActivePeriodsTestMock', {
    extend: 'Ext.data.Store',

    fields: ['id', 'short_name', 'parentnode__short_name', {
        "type": "date", 
        "name": "start_time", 
        "dateFormat": "Y-m-dTH:i:s"
    }],

    sorters: [{
        property : 'start_time',
        direction: 'DESC'
    }],

    data: [{
        id: 0,
        parentnode__short_name:'duck1100',
        short_name:'2011h',
        start_time: '2011-01-01T12:00:00'
    }, {
        id: 1,
        parentnode__short_name:'duck1100',
        short_name:'2012h',
        start_time: '2012-01-03T12:30:00'
    }, {
        id: 2,
        parentnode__short_name:'duck-mek2030',
        short_name:'2012h',
        start_time: '2012-01-16T01:30:00'
    }]
});
