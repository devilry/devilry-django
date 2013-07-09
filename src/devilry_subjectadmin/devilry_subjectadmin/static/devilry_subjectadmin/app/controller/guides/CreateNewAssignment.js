Ext.define('devilry_subjectadmin.controller.guides.CreateNewAssignment', {
    extend: 'devilry_subjectadmin.controller.guides.Base',

    views: [
        'guides.CreateNewAssignment'
    ],

    steps: 4,
    title: gettext('Create new assignment'),

    refs: [{
        ref: 'guideView',
        selector: 'viewport guide-createnewassignment'
    }, {
        ref: 'createNewAssignmentBox',
        selector: 'viewport periodoverview #createNewAssignmentBox'
    }],


    init: function() {
        this.callParent(arguments);
        this.control({
            'viewport guide-createnewassignment': {
                render: this.onRender
            },
            'viewport dashboard allactivewhereisadminlist': {
                render: this.ifActiveInterceptor(this.onFirstStep)
            },
            'viewport periodoverview #createNewAssignmentBox': {
                render: this.ifActiveInterceptor(this._onPeriodRender)
            },
            'viewport createnewassignment #pageOne': {
                render: this.ifActiveInterceptor(this._onCreateNewAssignmentPageOne),
                show: this.ifActiveInterceptor(this._onCreateNewAssignmentPageOne)
            },
            'viewport createnewassignment #pageTwo': {
                show: this.ifActiveInterceptor(this._onCreateNewAssignmentPageTwo)
            },
            'viewport createnewassignment #createButton': {
                click: this.ifActiveInterceptor(this._onCreateAssignmentClick)
            }
        });
    },

    onFirstStep: function() {
        this.getGuideView().getLayout().setActiveItem('dashboard');
        this.setStep('dashboard', 1);
    },

    _onPeriodRender: function() {
        this.setStep('period', 2);
        var element = this.getCreateNewAssignmentBox().getEl().down('a');
        Ext.defer(function() {
            this.guideSystem.pointAt(element);
        }, 500, this);
    },

    _onCreateNewAssignmentPageOne: function() {
        this.setStep('createnewassignment1', 3);
    },
    _onCreateNewAssignmentPageTwo: function() {
        this.setStep('createnewassignment2', 4);
    },

    _onCreateAssignmentClick: function() {
        this.guideSystem.endGuide();
    }
});
