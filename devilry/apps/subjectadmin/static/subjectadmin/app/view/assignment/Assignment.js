Ext.define('subjectadmin.view.assignment.Assignment' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.assignment',
    cls: 'assignment sidebarlayout',
    requires: [
        'themebase.layout.RightSidebar',
        //'subjectadmin.views.ActionList'
    ],

    layout: 'rightsidebar',
    frame: false,

    items: [{
        xtype: 'container',
        cls: 'centercolumn',
        region: 'main',
        items: [{
            xtype: 'actionlist',
            data: {
                title: 'Actions',
                links: [{
                    url: '#/@@create-new-assignment/@@chooseperiod',
                    text: 'Create new assignment'
                }, {
                    url: '#/',
                    text: 'Browse all'
                }, {
                    url: '#/@@register-for-final-exams',
                    text: 'Register students that qualify for final exams'
                }, {
                    url: '#/@@global-statistics',
                    text: 'Statistics'
                }]
            }
        }]
    }, {
        xtype: 'container',
        border: false,
        region: 'sidebar',
        items: [{
            xtype: 'box',
            html: 'Something'
        }]
    }]
});
