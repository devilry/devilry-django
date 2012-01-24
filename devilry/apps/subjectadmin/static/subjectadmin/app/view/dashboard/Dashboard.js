Ext.define('subjectadmin.view.dashboard.Dashboard' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.dashboard',
    cls: 'dashboard',

    layout: 'border',

    items: [{
        xtype: 'actionlist',
        region: 'center',
        data: {
            title: 'Actions',
            links: [{
                url: '#create-new-assignment',
                text: 'Create new assignment'
            }, {
                url: '#browse-all',
                text: 'Browse all'
            }, {
                url: '#register-for-final-exams',
                text: 'Register students that qualify for final exams'
            }, {
                url: '#global-statistics',
                text: 'Statistics'
            }]
        }
    }, {
        xtype: 'shortcutlist',
        region: 'east',
        width: 350
    }]
});
