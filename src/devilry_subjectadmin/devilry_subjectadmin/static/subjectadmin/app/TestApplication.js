Ext.define('subjectadmin.TestApplication', {
    extend: 'subjectadmin.Application',

    controllers: [
        'ShortcutsTestMock',
        'Dashboard',
        'CreateNewAssignmentTestMock',
        'subject.ListAllTestMock',
        'subject.OverviewTestMock',
        'period.OverviewTestMock',
        'assignment.OverviewTestMock',
        'assignment.EditPublishingTime',
        'assignment.EditAnonymous',
        'managestudents.OverviewTestMock',
        'managestudents.AddStudentsPlugin',
        'managestudents.NoGroupSelectedViewPlugin',
        'managestudents.SingleGroupSelectedViewPlugin',
        'managestudents.MultipleGroupsSelectedViewPlugin'
    ],

    setupExtraRoutes: function() {
        // These views are only for unit tests
        this.route.add("/@@dashboard/shortcutlist", 'shortcutlist');
        this.route.add("/@@dashboard/actionlist", 'actionlist');
    },


    /*********************************************
     * Only for testing.
     ********************************************/
    shortcutlist: function() {
        this.setPrimaryContent({xtype: 'shortcutlist'});
    },

    actionlist: function() {
        this.setPrimaryContent({
            xtype: 'actionlist',
            data: {
                title: 'Action list test',
                links: [{
                    url: '#/@@actionitem-1',
                    text: 'Action item 1'
                }, {
                    url: '#/@@actionitem-2',
                    text: 'Action item 2'
                }]
            }
        });
    }
});
