Ext.define('devilry_subjectadmin.controller.guides.CreateNewAssignment', {
    extend: 'devilry_subjectadmin.controller.guides.Base',

    views: [
        'guides.CreateNewAssignment'
    ],

    steps: 3,
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
            'viewport dashboard allactivewhereisadminlist': {
                render: Ext.Function.createInterceptor(this.onFirstStep, this.isActive)
            },
            'viewport periodoverview #createNewAssignmentBox': {
                render: Ext.Function.createInterceptor(this._onPeriodRender, this.isActive)
            }
        });
    },

    onFirstStep: function() {
        console.log('onFirstStep');
        this.getGuideView().getLayout().setActiveItem('dashboard');
        this.setStep('dashboard', 1);
    },

    _onPeriodRender: function() {
        console.log('_onPeriodRender');
        this.setStep('period', 2);
        var element = this.getCreateNewAssignmentBox().getEl().down('a');
        this.guideSystem.pointAt(element);
    }
});
