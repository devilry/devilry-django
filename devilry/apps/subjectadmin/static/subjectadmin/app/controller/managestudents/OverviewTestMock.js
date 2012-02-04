Ext.define('subjectadmin.controller.managestudents.OverviewTestMock', {
    extend: 'subjectadmin.controller.managestudents.Overview',

    requires: [
        'subjectadmin.model.GroupTestMock',
        'jsapp.HiddenElementProxy'
    ],

    stores: [
        'SingleAssignmentTestMock',
        'GroupsTestMock'
    ],


    /** Load week1 into the store. */
    _loadAssignmentsIntoStore: function() {
        var dateformat = 'Y-m-d\\TH:i:s';
        var now = Ext.Date.format(new Date(), dateformat);
        var initialData = [{
            id: 0,
            parentnode__parentnode__short_name:'duck1100',
            parentnode__short_name:'2012h',
            parentnode:2,
            long_name:'The one and only week one',
            publishing_time: now,
            short_name:'week1'
        }];

        // Add data to the proxy. This will be available in the store after a
        // load(), thus simulating loading from a server.
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.AssignmentTestMock', data);
            record.phantom = true; // Force create
            record.save();
        }, this);
    },

    /** Load groups into the store. */
    _loadGroupsIntoStore: function() {
        var initialData = [{
            "name": null,
            "tags": ['group1'],
            "students": [{
                "student__devilryuserprofile__full_name": "The Student0",
                "candidate_id": null,
                "student__username": "student0",
                "student__email": "student0@example.com"
            }],
            "feedback__is_passing_grade": null,
            "deadlines": [{
                "deadline": "2011-12-06T07:23:02"
            }],
            "examiners": [{
                "user__username": "examiner0",
                "user__email": "examiner0@example.com",
                "user__devilryuserprofile__full_name": null
            }],
            "feedback__points": null,
            "feedback__grade": null,
            "is_open": true,
            "feedback__save_timestamp": null,
            "id": 1
        }, {
            "name": null,
            "tags": ['group1'],
            "students": [{
                "student__devilryuserprofile__full_name": "The Student1",
                "candidate_id": null,
                "student__username": "student1",
                "student__email": "student1@example.com"
            }],
            "feedback__is_passing_grade": true,
            "deadlines": [{
                "deadline": "2011-12-06T07:23:02"
            }],
            "examiners": [{
                "user__username": "examiner0",
                "user__email": "examiner0@example.com",
                "user__devilryuserprofile__full_name": null
            }],
            "feedback__points": 14,
            "feedback__grade": "g14",
            "is_open": false,
            "feedback__save_timestamp": "2012-02-04T07:23:07",
            "id": 2
        }, {
            "name": null,
            "tags": [],
            "students": [{
                "student__devilryuserprofile__full_name": "The Student2",
                "candidate_id": null,
                "student__username": "student2",
                "student__email": "student2@example.com"
            }],
            "feedback__is_passing_grade": true,
            "deadlines": [{
                "deadline": "2011-12-06T07:23:02"
            }],
            "examiners": [{
                "user__username": "examiner0",
                "user__email": "examiner0@example.com",
                "user__devilryuserprofile__full_name": null
            }],
            "feedback__points": 14,
            "feedback__grade": "g14",
            "is_open": false,
            "feedback__save_timestamp": "2012-02-04T07:23:07",
            "id": 3
        }];


        // Add data to the proxy. This will be available in the store after a
        // load(), thus simulating loading from a server.
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.GroupTestMock', Ext.apply(data));
            record.phantom = true; // Force create
            record.save();
        }, this);
    },

    init: function() {
        this._loadAssignmentsIntoStore();
        this._loadGroupsIntoStore();
        this.callParent();
    },

    getSingleAssignmentStore: function() {
        return this.getSingleAssignmentTestMockStore();
    },

    getGroupsStore: function() {
        return this.getGroupsTestMockStore();
    }
});
