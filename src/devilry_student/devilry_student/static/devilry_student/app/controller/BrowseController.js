Ext.define('devilry_student.controller.BrowseController', {
    extend: 'Ext.app.Controller',

    views: [
        'browse.Browse',
        'browse.BrowseList',
        'browse.BrowseCalendar'
    ],

    stores: [
        'OpenGroupsDeadlineNotExpired',
        'OpenGroupsDeadlineExpired',
        'RecentDeliveries',
        'RecentFeedbacks',
        'FindGroups'
    ],

    refs: [{
        ref: 'browse',
        selector: 'viewport browse browselist'
    }],

    init: function() {
        this.control({
            'viewport browse': {
                render: this._onRenderList
            }
        });
    },

    _onRenderList: function() {
        console.log('Hei');
    }
});
