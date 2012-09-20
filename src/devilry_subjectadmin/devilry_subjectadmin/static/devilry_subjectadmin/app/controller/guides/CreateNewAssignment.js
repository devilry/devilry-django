Ext.define('devilry_subjectadmin.controller.guides.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    views: [
        'guides.CreateNewAssignment'
    ],

    refs: [{
        ref: 'guideView',
        selector: 'viewport guide-createnewassignment'
    }, {
        ref: 'createNewAssignmentBox',
        selector: 'viewport periodoverview #createNewAssignmentBox'
    }],

    init: function() {
        this.control({
            'viewport guide-createnewassignment': {
                render: this._onRender
            },
            'viewport dashboard': {
                render: this._onDashboardRender
            },
            'viewport periodoverview #createNewAssignmentBox': {
                render: this._onPeriodRender
            }
        });
    },

    _onRender: function() {
        this.guideSystem = this.getGuideView().guideSystem
        this.guideSystem.setTitle(gettext('Create new assignment'));
    },

    _onDashboardRender: function() {
        console.log('dash');
        this.guideSystem.setProgress(1, 3);
        this.getGuideView().getLayout().setActiveItem('dashboard');
    },

    _onPeriodRender: function() {
        console.log('period');
        this.guideSystem.setProgress(2, 3);
        this.getGuideView().getLayout().setActiveItem('period');
        var element = this.getCreateNewAssignmentBox().getEl().down('a');
        this.guideSystem.pointAt(element);
    }
});
