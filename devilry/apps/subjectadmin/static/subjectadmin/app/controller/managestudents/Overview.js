/**
 * Controller for the managestudents overview.
 */
Ext.define('subjectadmin.controller.managestudents.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'subjectadmin.utils.LoadAssignmentMixin'
    },

    views: [
        'managestudents.Overview',
        'managestudents.ListOfGroups'
    ],

    stores: [
        'SingleAssignment'
    ],

    refs: [{
        ref: 'overview',
        selector: 'managestudentsoverview'
    }],

    init: function() {
        this.control({
            'viewport managestudentsoverview': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.subject_shortname = this.getOverview().subject_shortname;
        this.period_shortname = this.getOverview().period_shortname;
        this.assignment_shortname = this.getOverview().assignment_shortname;
        this.loadAssignment();
    },

    getSubjectShortname: function() {
        return this.subject_shortname;
    },
    getPeriodShortname: function() {
        return this.period_shortname;
    },
    getAssignmentShortname: function() {
        return this.assignment_shortname;
    },

    getMaskElement: function() {
        return this.getOverview().getEl();
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        console.log('Assignment:', record.data);
        this.getGroupsStore().load();
    }
});
